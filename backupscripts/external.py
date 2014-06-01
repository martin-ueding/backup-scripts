#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2011-2014 Martin Ueding <dev@martin-ueding.de>

"""
Traverses through the external drives and updates the backup on them.
"""

import os
import subprocess

import termcolor

import backupscripts.status

__docformat__ = "restructuredtext en"

data_partitions = [
    "/media/mu/Gamma-data/home/mu/",
    "/media/mu/Sigma-data/home/mu/",
    "/media/mu/MU-3-466G-data/home/mu/",
    "Martin-Aspire-X3200.local:",
]

info_partitions = [
    "Gamma-info",
    "Sigma-info",
    "MU-3-466G-info",
]

infofiles = [
    os.path.expanduser("~/Dokumente/Listen/Hauptliste.kdb"),
    os.path.expanduser("~/Installer/Sicherheit/KeePass-1.15-Setup.exe"),
    os.path.expanduser("~/Installer/Sicherheit/KeePassX-0.4.0.dmg"),
]

def backup_data(name):
    """
    Creates a backup to ``target``.

    :param name: Name of this backup.
    :type name: str
    :param target: Target directory.
    :type target: str
    """
    excludesfile = os.path.expanduser("~/.config/backup-scripts/full.exclude.txt")

    source = os.path.expanduser("~/")

    target = name

    termcolor.cprint("Backup {}".format(name), attrs=['bold'])

    destdir = target

    if os.path.exists(excludesfile):
        exclude_arg = ["--exclude-from", excludesfile]
    else:
        exclude_arg = []

    command = ["rsync", "-avhE", "--delete", "--delete-excluded"] + exclude_arg + ["--", source, destdir]

    try:
        subprocess.check_call(command)
    except subprocess.CalledProcessError as e:
        print(e)
    else:
        backupscripts.status.update(name, 'to')

def backup_info(name):
    target = "/media/mu/{}/info/".format(name)

    if not os.path.isdir(target):
        return

    termcolor.cprint("Info {}".format(name), attrs=['bold'])

    command = ["rsync", "-avhE", "--delete", "--"] + infofiles + [target]

    try:
        subprocess.check_call(command)
    except subprocess.CalledProcessError as e:
        print(e)
    else:
        backupscripts.status.update(name, 'to')

def main():
    for name in info_partitions:
        backup_info(name)

    for name in data_partitions:
        backup_data(name)

if __name__ == "__main__":
	main()
