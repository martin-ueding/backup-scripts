#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2014 Martin Ueding <dev@martin-ueding.de>

'''
Exit codes
==========

10:
    Given device does not exist.

11:
    Given device is blacklisted.

12:
    Given device is mounted.
'''

import argparse
import tempfile
import os.path
import subprocess
import sys

import termcolor

blacklist = [
    '/dev/sda',
    '/dev/sdb',
]

def wrap_command(command, options):
    if options.sudo:
        command = ['sudo'] + command

    if options.english:
        command = ['env', 'LC_ALL=C'] + command

    print()
    print('----------------------------------')
    termcolor.cprint(' '.join(command), 'yellow', attrs=['bold'])
    print('----------------------------------')
    print()

    return command

def run_command(command, options):
    command = wrap_command(command, options)
    subprocess.check_call(command)

def main():
    options = _parse_args()

    if not os.path.exists(options.device):
        print('Given device ({}) does not exist. Exiting.'.format(options.device))
        sys.exit(10)

    if options.device in blacklist:
        print('Given device ({}) is blacklisted. Exiting.'.format(options.device))
        sys.exit(11)

    # Check mounts.
    output = subprocess.check_output(['mount'])
    if options.device.encode() in output:
        print('Given device ({}) is mounted. Exiting.'.format(options.device))
        sys.exit(12)


    command = wrap_command(['gdisk', options.device], options)

    gdisk_keys = [
        'p',     # Print partition table.
        'o',     # Create a new GPT partition table.
        'Y',     # YES.
        'p',     # Print partition table.
        'n',     # Create a new partition.
        '1',     # Make it the first.
        '',      # Default start sector.
        '+100M', # End at 100 MB.
        '',      # Default file system.
        'n',     # Create a new partition.
        '2',     # Make it the second.
        '',      # Default start.
        '',      # Default end.
        '',      # Default file system.
        'p',     # Print partition table.
        'w',     # Write to disk.
        'Y',     # YES.
    ]

    with tempfile.TemporaryFile('w+') as fdisk_input:
        for key in gdisk_keys:
            fdisk_input.write(key)
            fdisk_input.write('\n')
        fdisk_input.seek(0)

        subprocess.check_call(command, stdin=fdisk_input)

    info_device = options.device+'1'
    data_device = options.device+'2'

    if options.fs == 'btrfs':
        run_command(['mkfs.btrfs', '-f', '--mixed', '-L', '{}-info'.format(options.label), info_device], options)
        run_command(['mkfs.btrfs', '-f', '-L', '{}-data'.format(options.label), data_device], options)

        run_command(['btrfsck', info_device], options)
        run_command(['btrfsck', data_device], options)
    else:
        run_command(['mkfs.ext4', '-L', '{}-info'.format(options.label), info_device], options)
        run_command(['mkfs.ext4', '-L', '{}-data'.format(options.label), data_device], options)

        run_command(['fsck.ext4', info_device], options)
        run_command(['fsck.ext4', data_device], options)

    run_command(['mount', '-t', options.fs, info_device, '/mnt'], options)
    run_command(['mkdir', '/mnt/info'], options)
    run_command(['chown', 'mu:mu', '/mnt/info'], options)
    run_command(['ls', '-l', '/mnt/'], options)
    run_command(['umount', '/mnt'], options)

    run_command(['mount', '-t', options.fs, info_device, '/mnt'], options)
    run_command(['ls', '-l', '/mnt/'], options)
    run_command(['umount', '/mnt'], options)

    run_command(['mount', '-t', options.fs, data_device, '/mnt'], options)
    run_command(['mkdir', '/mnt/backup'], options)
    run_command(['chown', 'mu:mu', '/mnt/backup'], options)
    run_command(['ls', '-l', '/mnt/'], options)
    run_command(['umount', '/mnt'], options)

    run_command(['mount', '-t', options.fs, data_device, '/mnt'], options)
    run_command(['ls', '-l', '/mnt/'], options)
    run_command(['umount', '/mnt'], options)




def _parse_args():
    """
    Parses the command line arguments.

    :return: Namespace with arguments.
    :rtype: Namespace
    """
    parser = argparse.ArgumentParser(description='Provisions a backup hard drive.')
    parser.add_argument('device', help='Path to device, like /etc/sdd')
    parser.add_argument('label', help='Name for this disk')
    parser.add_argument('--sudo', action='store_true', help='Use sudo')
    parser.add_argument('--english', action='store_true', help='English output')
    parser.add_argument('--fs', default='btrfs')
    options = parser.parse_args()

    return options

if __name__ == "__main__":
    main()
