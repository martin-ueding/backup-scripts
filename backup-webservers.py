#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright © 2012 Martin Ueding <dev@martin-ueding.de>

import argparse
import yaml

__docformat__ = "restructuredtext en"

def main():
    options = _parse_args()

    load_servers("servers.yaml")


def load_servers(serverfile):
    """
    Loads the server data.

    :return: Server data.
    """
    with open(serverfile) as stream:
        data = yaml.load(stream)

    return data

def _parse_args():
    """
    Parses the command line arguments.

    :return: Namespace with arguments.
    :rtype: Namespace
    """
    parser = argparse.ArgumentParser(usage="", description="")
    parser.add_argument("args", metavar="N", type=str, nargs="*",
                   help="Positional arguments.")
    #parser.add_argument("", dest="", type="", default=, help=)
    #parser.add_argument("--version", action="version", version="<the version>")

    return parser.parse_args()


if __name__ == "__main__":
    main()
