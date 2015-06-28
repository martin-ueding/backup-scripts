#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2015 Martin Ueding <dev@martin-ueding.de>

import unittest

from backupscripts import todo

class TodoTests(unittest.TestCase):
    def test_1(self):
        r = toto.todo_to_taskwarrior('(B) 2015-06-07 Test')
        self.assertEqual(['add', 'pri:m', 'due:2015-06-07', 'Test'])
