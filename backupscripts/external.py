#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2011-2014 Martin Ueding <dev@martin-ueding.de>

"""
Traverses through the external drives and updates the backup on them.
"""

import configparser
import os
import re
import subprocess

import termcolor

import backupscripts.status

__docformat__ = "restructuredtext en"

def backup_data(key, name, config):
    """
    Creates a backup to ``target``.
    """
    excludes = []
    for exclude in config[key]['exclude'].split():
        excludes += config['exclude'][exclude].split(':')

    source = os.path.expanduser("~/")

    termcolor.cprint("Backup {}".format(name), attrs=['bold'])

    exclude_arg = []
    for exclude in excludes:
        exclude_arg.append('--exclude='+exclude)


    if 'host' in config[key]:
        dest = config[key]['host'] + ':' + config[key]['path']
        # TODO
        return
    else:
        dest = config[key]['path']
        if not os.path.isdir(dest):
            return

    command = ["rsync", "-avhE", "--delete", "--delete-excluded"] + exclude_arg + ["--", source, dest]

    try:
        subprocess.check_call(command)
    except subprocess.CalledProcessError as e:
        print(e)
    else:
        backupscripts.status.update(name, 'to')

def backup_info(key, name, config):
    target = config[key]['path']

    termcolor.cprint("Info {}".format(name), attrs=['bold'])

    if not os.path.isdir(target):
        return

    infofiles = [os.path.expanduser(path) for path in config['infofiles']['paths']]

    command = ["rsync", "-avhE", "--delete", "--"] + infofiles + [target]

    try:
        subprocess.check_call(command)
    except subprocess.CalledProcessError as e:
        print(e)
    else:
        backupscripts.status.update(name, 'to')

def main():
    config = configparser.ConfigParser()
    config.read(os.path.expanduser('~/.config/backup-scripts/backup-external.ini'))

    targets = [key.split()[-1] for key in config.sections() if key.startswith('Target')]
    infos = [key.split()[-1] for key in config.sections() if key.startswith('Info')]

    info_pattern = re.compile(r'Info (.*)')
    data_pattern = re.compile(r'Target (.*)')

    for key in config.sections():
        info_matcher = info_pattern.match(key)
        if info_matcher:
            backup_info(key, info_matcher.group(1), config)

        data_matcher = data_pattern.match(key)
        if data_matcher:
            backup_data(key, data_matcher.group(1), config)

if __name__ == "__main__":
    main()
