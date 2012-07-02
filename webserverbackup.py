#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright © 2012 Martin Ueding <dev@martin-ueding.de>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

"""
:author: Martin Ueding
:contact: dev@martin-ueding.de
:license: MIT

Creates backups from FTP servers and MySQL databases.

You can use the ``backup-webservers`` script with a configuration file (see
that script for more information). You can also just use this module and use it
in your own scripts.

dependencies
============

This module depends on the following things:

- You have ``curlftpfs`` as a program installed.
- There is a ``chmod`` and a ``chgrp`` program. I assume this is the case only
  on Linux and UNIX.
- Your user is in group ``fuse``.
"""

def backup_server(server):
    """
    Creates a backup of the given server.

    The following fields should (or can) be in the ``server`` dict:

    ``name``
        Name of the backup.
    ``backupdir``
        Where the backup has to go. ``os.path.expanduser()`` is called upon this
        value.
    ``server``
        URL to the FTP server. Should have a trailing slash.
    ``subfolder``
        (optional) If only a part of the FTP has to be copied. Should have a
        trailing slash.
    ``dump``
        (optional) HTTP URL to the MySQL dump script.
    ``dump-user``
        (optional) HTTP username for the dump script.
    ``dump-password``
        (optional) HTTP password for the dump script.

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
        server["tempdir"] = tempfile.mkdtemp(prefix="backup-webservers")
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
