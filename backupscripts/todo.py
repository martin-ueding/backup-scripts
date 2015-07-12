#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2015 Martin Ueding <dev@martin-ueding.de>

'''
Parser that converts ``todo.txt`` style lines into commands for Taskwarrior.
'''

import re


DONE = re.compile(r'^x (\d{4}-\d{2}-\d{2}) (.*)$')
PRIORITY = re.compile(r'\(([A-Z])\)')
ENTRY = re.compile(r'(\d{4}-\d{2}-\d{2})')
LIST = re.compile(r'@(\w+)')


def todo_to_taskwarrior(string):
    '''
    Takes a ``todo.txt`` like string and parses it to add to Taskwarrior.
    '''
    done, remainder = _split_done(string)

    if done == False:
        result = ['add']
    else:
        result = ['log', 'end:' + done]

    result += [_parse_bit(bit) for bit in remainder.split()]

    return result


def _split_done(string):
    m = DONE.search(string)

    if m:
        return m.group(1), m.group(2)
    else:
        return False, string


def _parse_bit(bit):
    m = PRIORITY.match(bit)
    if m:
        priority = m.group(1)
        return 'pri:' + {'A': 'h', 'B': 'm', 'C': 'l'}[priority]

    m = ENTRY.match(bit)
    if m:
        return 'entry:' + m.group(1)

    m = LIST.match(bit)
    if m:
        return 'pro:' + m.group(1)

    # Nothing special could be determined about this bit, so it must be just a
    # simple word.
    return bit
