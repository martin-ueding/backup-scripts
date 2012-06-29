#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright © 2012 Martin Ueding <dev@martin-ueding.de>

import argparse
import yaml

__docformat__ = "restructuredtext en"

def main():
    options = _parse_args()

    servers = load_servers("servers.yaml")

    for server in servers:
        backup_server(server)

def backup_server(server):
    """
    Creates a backup of the given server.

    :param server: Server data.
    :type server: dict
    """
    # Create mountpoint
    # Mount FTP volume
    # Copy all the files
    # Dump the MySQL database.
    # Create a .tar.gz archive with the current data.
    # Update the backup-status entry.


def load_servers(serverfile):
    """
    Loads the server data.

    :return: Server data.
    """
    with open(serverfile) as stream:
        data = yaml.load(stream)

    return data

def _parse_args():
    """
    Parses the command line arguments.

    :return: Namespace with arguments.
    :rtype: Namespace
    """
    parser = argparse.ArgumentParser(usage="", description="")
    parser.add_argument("args", metavar="N", type=str, nargs="*",
                   help="Positional arguments.")
    #parser.add_argument("", dest="", type="", default=, help=)
    #parser.add_argument("--version", action="version", version="<the version>")

    return parser.parse_args()


if __name__ == "__main__":
    main()
