#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2014-2015 Martin Ueding <dev@martin-ueding.de>

import argparse
import configparser
import datetime
import glob
import json
import logging
import os
import os.path
import shutil
import subprocess
import tempfile

import termcolor

import backupscripts.readinglist
import backupscripts.sshfs
import backupscripts.status
import backupscripts.todo


FOLDERFILE = os.path.expanduser('~/.config/backup-scripts/android-folders.js')

with open(FOLDERFILE) as f:
    FOLDERS = json.load(f)


def delete_bin_contents(self, bin):
    bin_path = self.path_to(bin)
    logging.debug('Path to bin: %s', bin_path)

def touch_file(self, path):
    command = ['touch', self.path_to(path)]
    subprocess.check_call(command)

def mkdir(self, path):
    command = ['mkdir', '-p', self.path_to(path)]
    subprocess.check_call(command)


def copy_bins(bins, dropfolder, target):
    termcolor.cprint('Copy Bins', 'cyan')
    for bin in bins:
        bin_path = os.path.join(target, bin)
        try:
            logging.info('Copying bin %s to computer', bin)
            shutil.copytree(bin_path, os.path.join(dropfolder, bin))

            contents = os.listdir(bin_path)
            for file in contents:
                path = os.path.join(bin_path, file)
                logging.debug('Deleting %s', path)
                if os.path.isfile(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    logging.error('Cannot delete %s', path)
        except FileNotFoundError:
            logging.error('Bin “%s” does not exist.', bin)
        except subprocess.CalledProcessError:
            logging.error('Bin “%s” does not exist.', bin)


def import_todo_items(mountpoint):
    termcolor.cprint('Importing TODO items', 'cyan')
    for todofile in FOLDERS['todofiles']:
        todopath = os.path.join(mountpoint, todofile)

        if not os.path.isfile(todopath):
            continue

        error = False
        with open(todopath) as h:
            for line in h:
                if len(line.strip()):
                    bits = backupscripts.todo.todo_to_taskwarrior(line)
                    try:
                        subprocess.check_call(['task'] + bits)
                        print(bits)
                    except subprocess.CalledProcessError as e:
                        termcolor.cprint('Error adding “{}”, {}:'.format(line, repr(bits)), 'red')
                        print(e)
                        error = True

        if not error:
            with open(todopath, 'w') as f:
                pass


def delete_shopping_list_downloads(tempdir):
    temp_download = os.path.join(tempdir, 'Download')

    if not os.path.isdir(temp_download):
        return

    files = glob.glob(os.path.join(temp_download, 'Einkaufsliste*.pdf'))

    for file_ in files:
        os.unlink(file_)

    if len(os.listdir(temp_download)) == 0:
        os.rmdir(temp_download)


def move_gpx_files(tempdir):
    temp_download = os.path.join(tempdir, 'Download')

    if not os.path.isdir(temp_download):
        return

    files = glob.glob(os.path.join(temp_download, '*.gpx'))

    for file_ in files:
        os.rename(file_, os.path.join(os.path.expanduser('~/Dokumente/Karten/Tracks/'), os.path.basename(file_)))

    if len(os.listdir(temp_download)) == 0:
        os.rmdir(temp_download)


def sync_device(mountpoint):
    now = datetime.datetime.now()
    prefix = 'mobile-sync_{year:d}-{month:02d}-{day:02d}_{hour:02d}-{minute:02d}-{second:02d}-'.format(
        year=now.year,
        month=now.month,
        day=now.day,
        hour=now.hour,
        minute=now.minute,
        second=now.second,
    )
    tempdir = tempfile.mkdtemp(prefix=prefix, dir=os.path.expanduser('~/TODO'))

    logging.debug("Files I see: %s", repr(os.listdir(mountpoint)))

    try:
        termcolor.cprint('Syncing {}'.format(mountpoint), 'white', attrs=['bold'])
        import_todo_items(mountpoint)
        copy_bins(FOLDERS['bins'], tempdir, mountpoint)
        delete_shopping_list_downloads(tempdir)
        move_gpx_files(tempdir)
    except:
        raise
    finally:
        tempdir_contents = os.listdir(tempdir)
        logging.debug('Contents of temporary directory: %s', tempdir_contents)
        if len(tempdir_contents) == 0:
            logging.info('Deleting temporary directory')
            os.rmdir(tempdir)


def main():
    options = _parse_args()

    if not options.offline:
        backupscripts.readinglist.main()

    with open(FOLDERFILE) as f:
        folders = json.load(f)

    config = configparser.ConfigParser()
    config.read(os.path.expanduser('~/.config/backup-scripts/android-devices.ini'))

    for device in options.devices:
        path = config[device]['path']

        if 'host' in config[device]:
            host = config[device]['host']
            user = config[device]['user']
            remote = '{}@{}:{}'.format(user, host, path)

            with backupscripts.sshfs.SSHfsWrapper(remote) as mountpoint:
                sync_device(mountpoint)
        else:
            sync_device(path)

        backupscripts.status.update(device, 'from')


def _parse_args():
    """
    Parses the command line arguments.

    If the logging module is imported, set the level according to the number of
    ``-v`` given on the command line.

    :return: Namespace with arguments.
    :rtype: Namespace
    """
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("devices", type=str, nargs="+", help="Devices to sync")
    parser.add_argument("-v", dest='verbose', action="count", help='Enable verbose output. Can be supplied multiple times for even more verbosity.')
    parser.add_argument("--offline")

    options = parser.parse_args()

    # Try to set the logging level in case the logging module is imported.
    if options.verbose == 1:
        logging.basicConfig(level=logging.INFO)
    elif options.verbose == 2:
        logging.basicConfig(level=logging.DEBUG)

    return options


if __name__ == "__main__":
    main()
