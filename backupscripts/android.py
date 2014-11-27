#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2014 Martin Ueding <dev@martin-ueding.de>

import abc
import argparse
import configparser
import datetime
import json
import logging
import os
import os.path
import subprocess
import tempfile

import termcolor

import backupscripts.status

FOLDERFILE = os.path.expanduser('~/.config/backup-scripts/android-folders.js')

class Target(object):
    __metaclass__ = abc.ABCMeta
    def __init__(self, hostname, basepath, backup=True, music=True):
        self.basepath = basepath
        self.backup = backup
        self.music = music
        self.hostname = hostname

    @abc.abstractmethod
    def path_to(self, suffix):
        pass

    @abc.abstractmethod
    def delete_bin_contents(self, bin):
        pass

    @abc.abstractmethod
    def touch_file(self, path):
        pass

    @abc.abstractmethod
    def mkdir(self, path):
        pass

class SSHTarget(Target):
    def __init__(self, hostname, basepath, ip, backup=True, music=True, user='shell'):
        super().__init__(hostname, basepath, backup, music)

        self.ip = ip
        self.user = user

    def path_to(self, suffix):
        return os.path.join('{user}@{ip}:{basepath}'.format(user=self.user, ip=self.ip, basepath=self.basepath), suffix)

    def delete_bin_contents(self, bin):
        command = ['ssh', '{}@{}'.format(self.user, self.ip), 'rm -rf /sdcard/{bin}/* /sdcard/{bin}/.??*'.format(bin=bin)]
        logging.debug('Deletion command: %s', command)
        subprocess.check_call(command)

    def touch_file(self, path):
        command = ['ssh', '{}@{}'.format(self.user, self.ip), 'touch', '/sdcard/'+path]
        subprocess.check_call(command)

    def mkdir(self, path):
        command = ['ssh', '{}@{}'.format(self.user, self.ip), 'mkdir', '-p', '/sdcard/'+path]
        subprocess.check_call(command)


class USBTarget(Target):
    def __init__(self, hostname, basepath, backup=True, music=True):
        super().__init__(hostname, basepath, backup, music)

    def path_to(self, suffix):
        return os.path.join(self.basepath, suffix)

    def delete_bin_contents(self, bin):
        bin_path = self.path_to(bin)
        logging.debug('Path to bin: %s', bin_path)
        contents = os.listdir(bin_path)
        for file in contents:
            path = os.path.join(bin_path, file)
            logging.debug('Deleting %s', path)
            os.remove(path)

    def touch_file(self, path):
        command = ['touch', self.path_to(path)]
        subprocess.check_call(command)

    def mkdir(self, path):
        command = ['mkdir', '-p', '/sdcard/'+self.path_to(path)]
        subprocess.check_call(command)


def copy_backupdirs(backupdirs, target):
    termcolor.cprint('Copy Backupdirs', 'cyan')
    for backupdir in backupdirs:
        target_folder = os.path.dirname(backupdir)
        target_path = target.path_to(target_folder) + '/'

        rsync([os.path.join(os.path.expanduser('~'), backupdir)], target_path, ['--delete', '--max-size=500M', '--exclude=*.bin', '--delete-excluded'])

def copy_bins(bins, dropfolder, target):
    termcolor.cprint('Copy Bins', 'cyan')
    for bin in bins:
        try:
            logging.info('Copying bin %s to computer', bin)
            rsync([target.path_to(bin)], dropfolder)
            target.delete_bin_contents(bin)
        except FileNotFoundError:
            logging.error('Bin “%s” does not exist.', bin)
        except subprocess.CalledProcessError:
            logging.error('Bin “%s” does not exist.', bin)

def copy_music(target):
    termcolor.cprint('Copy Music', 'cyan')
    source = os.path.expanduser("~/.cache/mp3_packer/128") + os.path.expanduser('~/Musik/Musik/')
    flags = ['--exclude-from', os.path.expanduser("~/.config/backup-scripts/handy_musik.txt")]
    rsync([source], target.path_to('Music'), flags)

def rsync(sources, target_path, additional_flags=[]):
    flags = ['--progress', '-h', '-l', '-m', '-r', '-v', '--size-only', '--ignore-errors', '--exclude=.thumbnails', '--copy-links'] + additional_flags
    command = ['rsync'] + flags + sources + [target_path]
    logging.info('rsync command: %s', ' '.join(command))
    subprocess.check_call(command)

def copy_reading_list(target):
    termcolor.cprint('Copy Reading List', 'cyan')
    source = os.path.expanduser("~/Leseliste/")
    target.mkdir('Leseliste')
    rsync([source], target.path_to('Leseliste/'), ['--delete', '--max-size=2G'])

def copy_wohnungsunterlagen(target):
    termcolor.cprint('Copy Wohnungsunterlagen', 'cyan')
    source = os.path.expanduser("~/Dokumente/Wohnung_Monschauer_Strasse")
    rsync([source], target.path_to('Dokumente/'), ['--delete', '--max-size=1G'])

def copy_studium_pdf_dirs(target, studium_pdf_dirs):
    termcolor.cprint('Copy Studium PDF dirs', 'cyan')
    copy_pdf_dirs(studium_pdf_dirs, target)

def copy_other_pdf_dirs(target, other_pdf_dirs):
    termcolor.cprint('Copy other PDF dirs', 'cyan')
    copy_pdf_dirs(other_pdf_dirs, target)

def copy_pdf_dirs(pdf_dirs, target):
    for pdf_dir in pdf_dirs:
        target.mkdir(pdf_dir)
        rsync(pdf_dirs, target.path_to(os.path.dirname(pdf_dir)) + '/',
              ['--include=*/', '--include=*.pdf',
               '--exclude=*', '--delete', '--delete-excluded']
             )

def import_todo_items(tempdir):
    termcolor.cprint('Importing TODO items', 'cyan')
    todofile = os.path.join(tempdir, 'TODO', 'todo.txt')

    if not os.path.isfile(todofile):
        return

    error = False
    with open(todofile) as h:
        for line in h:
            try:
                words = line.split()
                if len(words) > 0:
                    subprocess.check_call(['task', 'add'] + words)
            except subprocess.CalledProcessError as e:
                termcolor.cprint('Error adding “{}”:'.format(line), 'red')
                print(e)
                error = True

    if not error:
        os.remove(todofile)
        if len(os.listdir(os.path.dirname(todofile))) == 0:
            os.rmdir(os.path.dirname(todofile))

def sync_device(target, folders):
    now = datetime.datetime.now()
    prefix = 'android-sync-python_{year:d}-{month:02d}-{day:02d}_{hour:02d}-{minute:02d}-{second:02d}-'.format(
        year=now.year,
        month=now.month,
        day=now.day,
        hour=now.hour,
        minute=now.minute,
        second=now.second,
    )
    tempdir = tempfile.mkdtemp(prefix=prefix, dir=os.path.expanduser('~/TODO'))

    try:
        termcolor.cprint('Syncing {}'.format(target.hostname), 'white', attrs=['bold'])

        copy_bins(folders['bins'], tempdir, target)
        import_todo_items(tempdir)
        termcolor.cprint('Creating new todo.txt', 'cyan')
        target.touch_file('TODO/todo.txt')
        if target.backup:
            copy_backupdirs(folders['backupdirs'], target)
        else:
            copy_studium_pdf_dirs(target, folders['studium_pdf_dirs'])
        if target.music:
            copy_music(target)
        copy_other_pdf_dirs(target, folders['other_pdf_dirs'])
        copy_reading_list(target)

        backupscripts.status.update(target.hostname, 'to')

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

    with open(FOLDERFILE) as f:
        folders = json.load(f)

    os.chdir(os.path.expanduser('~'))

    config = configparser.ConfigParser()
    config.read(os.path.expanduser('~/.config/backup-scripts/android-devices.ini'))

    devices = {}

    for device in config.sections():
        backup = config[device].getboolean('backup')
        music = config[device].getboolean('music')
        path = config[device]['path']

        if 'host' in config[device]:
            host = config[device]['host']
            user = config[device]['user']
            devices[device] = SSHTarget(device, path, host, backup, music, user=user)
        else:
            devices[device] = USBTarget(device, path, backup, music)

    for device in options.devices:
        sync_device(devices[device], folders)

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

    options = parser.parse_args()

    # Try to set the logging level in case the logging module is imported.
    if options.verbose == 1:
        logging.basicConfig(level=logging.INFO)
    elif options.verbose == 2:
        logging.basicConfig(level=logging.DEBUG)

    return options

if __name__ == "__main__":
    main()
