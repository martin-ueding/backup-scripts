#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2015 Martin Ueding <dev@martin-ueding.de>

'''
Helpers for ``sshfs``.
'''

import subprocess
import tempfile


class SSHfsWrapper(object):
    def __init__(self, remote):
        self.remote = remote

    def __enter__(self):
        self.mountpoint = tempfile.TemporaryDirectory()
        subprocess.call(['sshfs', self.remote, self.mountpoint])

    def __exit__(self):
        subprocess.call(['fusermount', '-u', self.mountpoint])
        self.mountpoint.cleanup()
