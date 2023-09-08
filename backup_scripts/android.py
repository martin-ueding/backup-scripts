import argparse
import datetime
import itertools
import logging
import os.path
import pathlib
import re
import shutil
import subprocess
import tempfile
import tomllib
from typing import Dict, Optional

from backup_scripts.sshfs import MTPFSWrapper, SSHfsWrapper


class Task:
    def execute(self, device_base: pathlib.Path, host_base: pathlib.Path):
        raise NotImplementedError()

    def name(self) -> str:
        raise NotImplementedError()


class CopyToHost(Task):
    def __init__(self, source: str, destination: str = None):
        self.source = source
        self.destination = destination

    def execute(self, device_base: pathlib.Path, host_base: pathlib.Path):
        device_dir = device_base / self.source
        if not device_dir.exists():
            return
        if self.destination:
            target_dir = pathlib.Path(self.destination).expanduser()
        else:
            target_dir = host_base / self.source
            target_dir.mkdir(parents=True, exist_ok=True)
        for path in device_dir.iterdir():
            if path.name in [".thumbnails"]:
                continue
            print(f"  Moving {path} to {target_dir}")
            shutil.move(path, target_dir)

    def name(self) -> str:
        return f"CopyToHost: {self.source}"


class CopyToDevice(Task):
    def __init__(self, source: str, destination: str, delete: bool = False):
        self.source = pathlib.Path(source).expanduser()
        self.destination = pathlib.Path(destination)
        self.delete = delete

    def execute(self, device_base: pathlib.Path, host_base: pathlib.Path):
        target_dir = device_base / self.destination
        target_dir.mkdir(exist_ok=True, parents=True)
        if self.source.is_file():
            copy_if_newer(self.source, self.source.parent, target_dir)
        else:
            command = ["rsync", "-avh"]
            if self.delete:
                command.append("--delete")
            command.extend(["--", str(self.source), str(target_dir.parent)])
            subprocess.run(command, check=True)

    def name(self) -> str:
        return f"CopyToDevice: {self.source}"


class CopyPictures(Task):
    def __init__(self, source: str, destination: str):
        self.source = pathlib.Path(source)
        self.destination = pathlib.Path(destination).expanduser()

    def execute(self, device_base: pathlib.Path, host_base: pathlib.Path):
        device_dir = device_base / self.source
        if not device_dir.exists():
            return
        for path in device_dir.iterdir():
            intermediate_target = self.destination / path.name
            shutil.move(path, intermediate_target)
            timestamp = self.extract_filename_img(intermediate_target)
            assert timestamp is not None
            new_name = self.make_filename(intermediate_target, timestamp)
            print(f"  Moving {path} to {new_name}")
            shutil.move(intermediate_target, new_name)

    def name(self) -> str:
        return f"CopyToDevice: {self.source}"

    @staticmethod
    def extract_filename_img(path: pathlib.Path) -> Optional[datetime.datetime]:
        if m := re.search(r"(20\d{2})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})", path.name):
            numbers = [int(g) for g in m.groups()]
            if numbers[3] == 24:
                numbers[3] = 0
            return datetime.datetime(*numbers)

        print(f"  Cannot parse {path}")

    @staticmethod
    def make_filename(path: pathlib.Path, timestamp: datetime.datetime):
        new_stem_base = f"{timestamp.year:04d}-{timestamp.month:02d}-{timestamp.day:02d}_{timestamp.hour:02d}-{timestamp.minute:02d}-{timestamp.second:02d}"
        for i in itertools.count():
            new_stem = new_stem_base
            if i > 0:
                new_stem += f"-{i}"
            new_path = path.with_stem(new_stem)
            if not new_path.exists():
                return new_path


def copy_if_newer(src: pathlib.Path, src_base: pathlib.Path, target_dir: pathlib.Path):
    target_file = target_dir / src.relative_to(src_base)
    if not target_file.exists() or src.stat().st_mtime > target_file.stat().st_mtime:
        print(f"  Copying {src} to {target_dir}")
        shutil.copy(src, target_dir)


def delete_empty_dirs(path):
    # Iterate through all the elements in the current path.
    contents = os.listdir(path)
    for element in contents:
        element_path = os.path.join(path, element)
        if os.path.isdir(element_path):
            delete_empty_dirs(element_path)

    # Delete the current directory if it is empty now.
    if len(os.listdir(path)) == 0:
        logging.debug("Deleting %s.", path)
        os.rmdir(path)


def copy_bins(bins, dropfolder, target):
    print("Copy Bins")
    for bin in bins:
        bin_path = os.path.join(target, bin)
        try:
            logging.info("Copying bin %s to computer", bin)
            shutil.copytree(bin_path, os.path.join(dropfolder, bin))

            contents = os.listdir(bin_path)
            for file in contents:
                path = os.path.join(bin_path, file)
                logging.debug("Deleting %s", path)
                if os.path.isfile(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    logging.error("Cannot delete %s", path)
        except FileNotFoundError:
            logging.error("Bin “%s” does not exist.", bin)
        except subprocess.CalledProcessError:
            logging.error("Bin “%s” does not exist.", bin)


def make_sync_directory() -> pathlib.Path:
    now = datetime.datetime.now()
    prefix = "mobile-sync_{year:d}-{month:02d}-{day:02d}_{hour:02d}-{minute:02d}-{second:02d}-".format(
        year=now.year,
        month=now.month,
        day=now.day,
        hour=now.hour,
        minute=now.minute,
        second=now.second,
    )
    tempdir = tempfile.mkdtemp(prefix=prefix, dir=os.path.expanduser("~/TODO"))
    return pathlib.Path(tempdir)


def task_factory(task_dict: Dict) -> Task:
    registry = {
        "CopyToHost": CopyToHost,
        "CopyToDevice": CopyToDevice,
        "CopyPictures": CopyPictures,
    }
    task_name = task_dict["type"]
    task_type = registry[task_name]
    other_args = {key: value for key, value in task_dict.items() if key != "type"}
    return task_type(**other_args)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("device")
    parser.add_argument("--mtp", action="store_true")
    options = parser.parse_args()

    config_path = pathlib.Path("~/.config/backup-scripts/android.toml").expanduser()
    with open(config_path, "rb") as f:
        config = tomllib.load(f)

    tasks = {
        task_name: task_factory(task_dict)
        for task_name, task_dict in config["tasks"].items()
    }

    selected_tasks = [
        tasks[task_name] for task_name in config["device"][options.device]["tasks"]
    ]

    host_base = make_sync_directory()

    if options.mtp:
        fs_wrapper = MTPFSWrapper()
    else:
        remote = "{user}@{host}:{path}".format(**config["device"][options.device])
        fs_wrapper = SSHfsWrapper(remote)
    with fs_wrapper as mount_point:
        print(f"Mounted at: {mount_point}")
        for task in selected_tasks:
            print(task.name())
            task.execute(mount_point, host_base)
        delete_empty_dirs(host_base)


if __name__ == "__main__":
    main()
