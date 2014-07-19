#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2011-2014 Martin Ueding <dev@martin-ueding.de>

"""
Traverses through the external drives and updates the backup on them.
"""

import argparse
import configparser
import os
import re
import subprocess

import termcolor

import backupscripts.status

__docformat__ = "restructuredtext en"

CONFIG_DIR = os.path.expanduser('~/.config/backup-scripts')

def backup_data(key, name, config, dry):
    """
    Creates a backup to ``target``.
    """
    excludes = []
    for exclude in config[key]['exclude'].split():
        filename = os.path.join(CONFIG_DIR, 'exclude', exclude + '.txt')
        with open(filename) as f:
            for line in f:
                path = line.strip()
                if len(path) > 0:
                    excludes.append(path)

    exclude_arg = []
    for exclude in excludes:
        exclude_arg.append('--exclude='+exclude)

    sources = []
    for include in config[key]['include'].split():
        filename = os.path.join(CONFIG_DIR, 'include', include + '.txt')
        with open(filename) as f:
            for line in f:
                path = line.strip()
                if len(path) > 0:
                    sources.append(path)

    termcolor.cprint("Backup {}".format(name), attrs=['bold'])

    for source in sources:
        termcolor.cprint('Handling {}'.format(source), 'cyan')
        rel_dest = os.path.dirname(source)
        abs_dest_path = os.path.join(config[key]['path'], rel_dest)

        if 'host' in config[key]:
            dest = config[key]['host'] + ':' + abs_dest_path
        else:
            dest = abs_dest_path
            if not os.path.isdir(dest):
                return

        command = ["rsync", "-avhE", "--delete", "--delete-excluded"]
        if dry:
            command.append('-n')
        command += exclude_arg + ["--", source, dest]

        print(command)

        try:
            subprocess.check_call(command)
        except subprocess.CalledProcessError as e:
            print(e)
            return

    if not dry:
        backupscripts.status.update(name, 'to')

def backup_info(key, name, config, dry):
    target = config[key]['path']

    termcolor.cprint("Info {}".format(name), attrs=['bold'])

    if not os.path.isdir(target):
        return

    infofiles = [os.path.expanduser(path) for path in config['infofiles']['paths'].split(':')]

    command = ["rsync", "-avhE", "--delete"]
    if dry:
        command.append('-n')
    command += ["--"] + infofiles + [target]

    try:
        subprocess.check_call(command)
    except subprocess.CalledProcessError as e:
        print(e)
    else:
        if not dry:
            backupscripts.status.update(name, 'to')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('names', nargs='*')
    parser.add_argument('-n', dest='dry', action='store_true')
    options = parser.parse_args()

    os.chdir(os.path.expanduser('~'))

    config = configparser.ConfigParser()
    config.read(os.path.join(CONFIG_DIR, 'backup-external.ini'))

    targets = [key.split()[-1] for key in config.sections() if key.startswith('Target')]
    infos = [key.split()[-1] for key in config.sections() if key.startswith('Info')]

    info_pattern = re.compile(r'Info (.*)')
    data_pattern = re.compile(r'Target (.*)')


    for key in config.sections():
        info_matcher = info_pattern.match(key)
        if info_matcher:
            backup_info(key, info_matcher.group(1), config, options.dry)

    for key in config.sections():
        data_matcher = data_pattern.match(key)
        if data_matcher:
            name = data_matcher.group(1)
            if len(options.names) == 0 or name in options.names:
                backup_data(key, name, config, options.dry)

if __name__ == "__main__":
    main()
