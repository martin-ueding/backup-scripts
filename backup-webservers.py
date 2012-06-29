#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright © 2012 Martin Ueding <dev@martin-ueding.de>

import argparse
import os.path
import subprocess
import tempfile
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
    print server

    current = os.path.join(os.path.expanduser(server["backupdir"]), server["name"])
    print "Creating backup into “{dir}”.".format(dir=current)

    # Make sure that the destination directory is created.
    if not os.path.isdir(current):
        os.makedirs(current)

    # Create mountpoint
    tempdir = tempfile.mkdtemp()
    subprocess.check_call(["chgrp", "fuse", "--", tempdir])
    subprocess.check_call(["chmod", "700", "--", tempdir])

    print "Using “{dir}” as mount point.".format(dir=tempdir)

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
