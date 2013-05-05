#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2012-2013 Martin Ueding <dev@martin-ueding.de>

from distutils.core import setup

setup(
    author="Martin Ueding",
    author_email="dev@martin-ueding.de",
    name="backup_scripts",
    py_modules=["webserverbackup"],
    scripts=[
        "android-sync",
        "backup-external",
        "backup-hauptliste",
        "backup-status",
        "backup-webserver",
        "backup-webservers",
    ],
    version="1.4",
)
