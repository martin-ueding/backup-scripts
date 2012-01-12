#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2012 Martin Ueding <dev@martin-ueding.de>

"""
Pretty prints tables.
"""

__docformat__ = "javadoc en"

def print_table(headers, data, margin=2):
    """
    Prints a table with header and data.

    @param headers List of column headers.
    @param data List of rows which are lists of columns.
    @param margin Spacing between columns-
    """
    margin -= 1
    headers_str = map(str, headers)
    data_str = [map(str, line) for line in data]

    col_widths = [max(len(headers_str[i]), max([len(row[i]) for row in data_str])) for i in range(len(headers))]

    for i in range(len(col_widths)):
        print headers_str[i].ljust(col_widths[i])+' '*margin,

    print

    for i in range(len(col_widths)):
        print ('-'*len(headers_str[i])).ljust(col_widths[i])+' '*margin,

    print

    for row in data_str:
        for i in range(len(col_widths)):
            print row[i].ljust(col_widths[i])+' '*margin,

        print
