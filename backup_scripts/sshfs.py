#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2015, 2018 Martin Ueding <martin-ueding.de>

'''
Helpers for ``sshfs``.
'''
import pathlib
import subprocess
import tempfile


class SSHfsWrapper(object):
    def __init__(self, remote):
        self.remote = remote

    def __enter__(self) -> pathlib.Path:
        self.mountpoint = tempfile.TemporaryDirectory()
        subprocess.run(['sshfs', '-o', 'reconnect', self.remote, self.mountpoint.name], check=True)
        return pathlib.Path(self.mountpoint.name)

    def __exit__(self, exc_type, exc_value, traceback):
        subprocess.run(['fusermount', '-u', self.mountpoint.name], check=True)
        self.mountpoint.cleanup()
