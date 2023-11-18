import subprocess
import pathlib
import tomllib
import shlex
import argparse


def backup_data(
    destination: pathlib.Path,
    includes: list[str],
    excludes: list[str],
    rsync_options: list[str],
) -> None:
    command = ["rsync", "-avhER", "--delete", "--delete-excluded"] + rsync_options
    command += (
        [f"--exclude={exclude}" for exclude in excludes]
        + ["--"]
        + includes
        + [str(destination)]
    )

    print(shlex.join(command))
    subprocess.run(command, check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", dest="dry", action="store_true")
    options = parser.parse_args()

    with open(
        pathlib.Path("~/.config/backup-scripts/backup-external.toml").expanduser(), "rb"
    ) as f:
        config = tomllib.load(f)

    for target_name, target_spec in config["target"].items():
        excludes = [
            path
            for exclude_name in target_spec["exclude"]
            for path in config["exclude"][exclude_name]
        ]
        includes = [
            path
            for include_name in target_spec["include"]
            for path in config["include"][include_name]
        ]

        destination = pathlib.Path(target_spec["path"])
        rsync_options = target_spec.get("rsync-options", [])
        if options.dry:
            rsync_options.append("-n")
        if destination.exists():
            print(f"Creating backup of {target_name} …")
            backup_data(destination, includes, excludes, rsync_options)
            print(f"Done with backup of {target_name}.")


if __name__ == "__main__":
    main()
