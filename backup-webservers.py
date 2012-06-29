#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright © 2012 Martin Ueding <dev@martin-ueding.de>

import argparse
import datetime
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

    server["backupdir"] = os.path.expanduser(server["backupdir"])
    server["current"] = os.path.join(server["backupdir"], server["name"])

    print "Creating backup into “{dir}”.".format(dir=server["current"])

    # Make sure that the destination directory is created.
    if not os.path.isdir(server["current"]):
        os.makedirs(server["current"])

    copy_data(server)
    dump_database(server)
    create_archive(server)

def copy_data(server):
    try:
        # Create mountpoint
        server["tempdir"] = tempfile.mkdtemp()
        subprocess.check_call(["chgrp", "fuse", server["tempdir"]])
        subprocess.check_call(["chmod", "700", server["tempdir"]])

        print "Using “{dir}” as mount point.".format(dir=server["tempdir"])

        # Mount FTP volume
        print "Mounting “{ftp}”.".format(ftp=server["server"])
        subprocess.check_call(["curlftpfs", server["server"], server["tempdir"]])

        # Copy all the files
        print "Copying all the files."

        if "subfolder" in server:
            subfolder = server["tempdir"] + "/" + server["subfolder"] + "/"
        else:
            subfolder = server["tempdir"] + "/"

        subprocess.check_call(["rsync", "-avE", "--delete",
                               subfolder, server["current"]+"/"])

    finally:
        subprocess.check_call(["fusermount", "-u", server["tempdir"]])

def dump_database(server):
    """
    Dump the MySQL database.
    """
    if "dump" in server:
        print "Dumping MySQL server via “{url}”.".format(url=server["dump"])

        sqlfile = os.path.join(server["current"], "dump.sql")
        subprocess.check_call(["wget", "--user", server["dump-user"],
                               "--password", server["dump-password"], "-O",
                               sqlfile, server["dump"]])

def create_archive(server):
    """
    Create a .tar.gz archive with the current data.
    """
    today = datetime.date.today()
    destdir = os.path.join(
        server["backupdir"],
        "{y:04d}-{m:02d}".format(y=today.year, m=today.month),
    )
    print "The archive is going into “{dir}”.".format(dir=destdir)

    if not os.path.isdir(destdir):
        os.makedirs(destdir)

    archivename = "{name}-{y:04d}{m:02d}{d:02d}.tar.gz".format(
        name = server["name"],
        y = today.year,
        m = today.month,
        d = today.day,
    )

    print "Creating “{tar}”.".format(tar=archivename)
    subprocess.check_call(["tar", "-czf", os.path.join(destdir, archivename),
                           "-C", server["backupdir"], server["name"]])

def update_status(server):
    """
    Update the backup-status entry.
    """
    subprocess.check_call(["backup-status", "update", server["name"]])

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
