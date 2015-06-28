#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2015 Martin Ueding <dev@martin-ueding.de>

import re

def todo_to_taskwarrior(string):
    '''
    Takes a ``todo.txt`` like string and parses it to add to Taskwarrior.
    '''
    
