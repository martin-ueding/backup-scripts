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

    termcolor.cprint('Command to be executed:', 'yellow')
    termcolor.cprint(' '.join(command), 'yellow')

    return command

def main():
    options = _parse_args()

    if not os.path.exists(options.device):
        print('Given device ({}) does not exist. Exiting.'.format(options.device))
        sys.exit(10)

    if options.device in blacklist:
        print('Given device ({}) is blacklisted. Exiting.'.format(options.device))
        sys.exit(11)


    command = wrap_command(['fdisk', options.device], options)

    with tempfile.TemporaryFile('w+') as fdisk_input:
        fdisk_input.write('''
                          p
                          o
                          p
                          n



                          +100M
                          n




                          p
                          w
                          ''')
        fdisk_input.seek(0)

        subprocess.check_call(command, stdin=fdisk_input)




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
    options = parser.parse_args()

    return options

if __name__ == "__main__":
    main()
