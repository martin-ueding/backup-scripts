#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2011-2014 Martin Ueding <martin-ueding.de>

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

STATUSFILE = os.path.expanduser("~/.local/share/backup-scripts/backup-status.js")

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

    if options.update is not None:
        update(options.update, options.direction)
    else:
        pretty(load_data(), options.direction)

def load_data():
    # Open the already existing file
    if os.path.exists(STATUSFILE):
        with open(STATUSFILE, "r") as f:
            status = json.loads(f.read())
    else:
        status = []

    return status

def save_data(status):
    with open(STATUSFILE, "w") as f:
        f.write(json.dumps(status, sort_keys=True, indent=4))

def update(backup, direction):
    status = load_data()

    if not backup in [x["name"] for x in status]:
        status.append({"name": backup})

    for status_row in status:
        # XXX Should have used a dict for this in first place.
        if not status_row["name"] == backup:
            continue

        status_row["last"] = str(datetime.datetime.now())
        
        if direction is not None:
            status_row["type"] = direction

    save_data(status)

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
