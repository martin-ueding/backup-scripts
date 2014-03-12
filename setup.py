#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2014 Martin Ueding <dev@martin-ueding.de>

from setuptools import setup, find_packages

__docformat__ = "restructuredtext en"

setup(
    author = "Martin Ueding",
    author_email = "dev@martin-ueding.de",
    description = "Collection of backup scripts",
    license = "GPL2",
    classifiers=[
        "Environment :: Console",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Programming Language :: Python",

    ],
    name = "backup-scripts",
    packages = find_packages(),
    entry_points = {
        'console_scripts': [
            'android-sync = backupscripts.android:main',
            'backup-externel = backupscripts.external:main',
            'backup-status = backupscripts.status:main',
        ],
    },
    install_requires=[
        'termcolor',
    ],
    scripts=[
        'backup-chaos',
    ],
    url = "https://github.com/martin-ueding/backup-scripts",
    download_url="http://martin-ueding.de/download/backup-scripts/",
    version = "1.17.1",
)
