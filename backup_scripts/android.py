import argparse
import datetime
import logging
import os.path
import pathlib
import shutil
import subprocess
import tempfile
import tomllib
from typing import Dict

import backup_scripts.sshfs


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
            for path in self.source.iterdir():
                copy_if_newer(path, self.source, target_dir)
            if self.delete:
                for path in target_dir.iterdir():
                    corresponding_source = self.source / path.name
                    if not corresponding_source.exists():
                        print(f"  Deleting {path}")
                        path.unlink()

    def name(self) -> str:
        return f"CopyToDevice: {self.source}"


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
    }
    task_name = task_dict["type"]
    task_type = registry[task_name]
    other_args = {key: value for key, value in task_dict.items() if key != "type"}
    return task_type(**other_args)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("device")
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
    remote = "{user}@{host}:{path}".format(**config["device"][options.device])
    with backup_scripts.sshfs.SSHfsWrapper(remote) as mount_point:
        print(f"Mounted at: {mount_point}")
        for task in selected_tasks:
            print(task.name())
            task.execute(mount_point, host_base)
        delete_empty_dirs(host_base)


if __name__ == "__main__":
    main()
