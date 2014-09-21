#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2014 Martin Ueding <dev@martin-ueding.de>

import argparse

blacklist = [
    '/dev/sda',
    '/dev/sdb',
]

def main():
    options = _parse_args()

def _parse_args():
    """
    Parses the command line arguments.

    :return: Namespace with arguments.
    :rtype: Namespace
    """
    parser = argparse.ArgumentParser(description='Provisions a backup hard drive.')
    parser.add_argument('device', help='Path to device, like /etc/sdd')
    parser.add_argument('label', help='Name for this disk')
    options = parser.parse_args()

    return options

if __name__ == "__main__":
    main()
