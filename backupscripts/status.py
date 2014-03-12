#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2011-2013 Martin Ueding <dev@martin-ueding.de>

"""
Gives a status summary for the backups.
"""

from prettytable import PrettyTable
import argparse
import datetime
import dateutil.parser
import json
import os


__docformat__ = "restructuredtext en"

def pretty(status, direction_filter):
    """
    Pretty format the backup status.

    :param status: List with status dicts.
    :type status: dict
    """
    status = sorted(status, key=lambda backup: backup["last"])

    data = []

    for s in status:
        if "type" in s:
            if s["type"] == "to":
                if direction_filter is not None and direction_filter != "to":
                    continue
                direction = " >"
            elif s["type"] == "from":
                if direction_filter is not None and direction_filter != "from":
                    continue
                direction = "< "
            elif s["type"] == "both":
                direction = "<>"
            else:
                direction = "??"
        else:
            direction = "??"

        name = s["name"]
        last = s["last"]
        last_date = dateutil.parser.parse(last)
        difference = datetime.datetime.now() - last_date

        data.append([direction, name, last_date, difference])

    if len(data) > 0:
        t = PrettyTable(["Dir", "Name", "Last", "Difference"])
        for row in data:
            t.add_row(row)
        t.align["Name"] = "l"
        t.align["Dir"] = "c"
        t.align["Difference"] = "r"
        print(t)


def main():
    options = _parse_args()

    changed = False

    statusfile = os.path.expanduser("~/.local/share/backup-scripts/backup-status.js")

    # Open the already existing file
    if os.path.exists(statusfile):
        with open(statusfile, "r") as f:
            status = json.loads(f.read())
    else:
        status = []


    if options.update is not None:
        backup = options.update

        if not backup in [x["name"] for x in status]:
            status.append({"name": backup})

        for s in status:
            if not s["name"] == backup:
                continue

            s["last"] = str(datetime.datetime.now())
            changed = True
            
            if options.direction is not None:
                s["type"] = options.direction

    else:
        pretty(status, options.direction)


    if changed:
        with open(statusfile, "w") as f:
            f.write(json.dumps(status, sort_keys=True, indent=4))

def _parse_args():
    """
    Parses the command line arguments.

    :return: Namespace with arguments.
    :rtype: Namespace
    """
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--update", metavar='NAME', help='Update the given backup.')
    parser.add_argument("--direction", help='Filter the direction, or set the direction the updated backup.')
    #parser.add_argument("--version", action="version", version="<the version>")

    return parser.parse_args()



if __name__ == "__main__":
	main()
