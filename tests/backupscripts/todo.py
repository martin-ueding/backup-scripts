#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2015 Martin Ueding <dev@martin-ueding.de>

import unittest

from backupscripts import todo


class TodoTests(unittest.TestCase):
    def test_1(self):
        r = todo.todo_to_taskwarrior('(B) 2015-06-07 Test')
        self.assertEqual(r, ['add', 'pri:m', 'entry:2015-06-07', 'Test'])

    def test_done(self):
        r = todo.todo_to_taskwarrior('x 2015-06-20 (B) 2015-06-07 Test')
        self.assertEqual(r, ['log', 'end:2015-06-20', 'pri:m', 'entry:2015-06-07', 'Test'])


class SplitDone(unittest.TestCase):
    def test_done(self):
        done, remainder = todo._split_done('x 2015-06-20 (B) 2015-06-07 Test')

        self.assertEqual(done, '2015-06-20')
        self.assertEqual(remainder, '(B) 2015-06-07 Test')

    def test_pending(self):
        done, remainder = todo._split_done('(B) 2015-06-07 Test')

        self.assertEqual(done, False)
        self.assertEqual(remainder, '(B) 2015-06-07 Test')
