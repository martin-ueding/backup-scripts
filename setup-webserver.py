#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright © 2012 Martin Ueding <dev@martin-ueding.de>

from distutils.core import setup

setup(
    author = "Martin Ueding",
    author_email = "dev@martin-ueding.de",
    description = "Creates backups of FTP servers.",
    license = "MIT"
    name = "backupwebservers",
    scripts = ["backup-webservers"],
    version = "1.0",
)
