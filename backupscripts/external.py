#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2011-2016 Martin Ueding <dev@martin-ueding.de>

"""
Traverses through the external drives and updates the backup on them.
"""

import argparse
import configparser
import os
import re
import subprocess

import backupscripts.status

__docformat__ = "restructuredtext en"

CONFIG_DIR = os.path.expanduser('~/.config/backup-scripts')

def read_shards(shard_names, shard_type):
    shards = []
    for shard in shard_names:
        filename = os.path.join(CONFIG_DIR, shard_type, shard + '.txt')
        with open(filename) as f:
            shards += f.read().strip().split('\n')

    shards.sort()

    return shards


def read_excludes(exclude_names):
    return read_shards(exclude_names, 'exclude')


def read_includes(include_names):
    return read_shards(include_names, 'include')


def backup_data(key, name, config, dry):
    """
    Creates a backup to ``target``.
    """
    excludes = read_excludes(config[key]['exclude'].split())
    exclude_arg = ['--exclude='+exclude for exclude in excludes]
    sources = read_includes(config[key]['include'].split())

    print("Backup {}".format(name), attrs=['bold'])

    abs_dest_path = config[key]['path']
    if 'host' in config[key]:
        dest = config[key]['host'] + ':' + abs_dest_path
    else:
        dest = abs_dest_path
        if not os.path.isdir(dest):
            print('This directory does not exist. Trying to create it …')
            try:
                os.makedirs(dest, exist_ok=True)
            except PermissionError as e:
                print(str(e), 'yellow')
                return


    command = ["rsync", "-avhER", "--delete", "--delete-excluded"]
    if dry:
        command.append('-n')
    if 'rsync-options' in config[key]:
        command += config[key]['rsync-options'].split()
    if 'only-formats' in config[key]:
        command.append('--include=*/')
        for suffix in config[key]['only-formats'].split():
            command.append('--include=*.{}'.format(suffix.lower()))
            command.append('--include=*.{}'.format(suffix.upper()))
        command.append('--exclude=*')
    command += exclude_arg + ["--"] + sources + [dest]

    print(command)

    try:
        subprocess.check_call(command)
    except subprocess.CalledProcessError as e:
        print(e)
        return
    else:
        if not dry:
            backupscripts.status.update(name, 'to')


def compute_total_size(key, config):
    sources = read_includes(config[key]['include'].split())
    exclude_args = [
        '--exclude-from='+os.path.join(CONFIG_DIR, 'exclude', f+'.txt')
        for f in config[key]['exclude'].split()
    ]
    subprocess.check_call(['du', '-csh'] + exclude_args + sources)



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('names', nargs='*')
    parser.add_argument('-n', dest='dry', action='store_true')
    parser.add_argument('--size', dest='size', action='store_true')
    options = parser.parse_args()

    os.chdir(os.path.expanduser('~'))

    config = configparser.ConfigParser()
    config.read(os.path.join(CONFIG_DIR, 'backup-external.ini'))

    targets = [key.split()[-1] for key in config.sections() if key.startswith('Target')]

    data_pattern = re.compile(r'Target (.*)')

    for key in config.sections():
        data_matcher = data_pattern.match(key)
        if data_matcher:
            name = data_matcher.group(1)
            if len(options.names) == 0 or name in options.names:
                if options.size:
                    compute_total_size(key, config)
                else:
                    backup_data(key, name, config, options.dry)


if __name__ == "__main__":
    main()
