#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2014-2015 Martin Ueding <dev@martin-ueding.de>

import configparser
import glob
import os.path
import re
import shutil

import lxml.html
import requests

DIR = os.path.expanduser('~/Leseliste')

def get_urls():
    urls = []

    files = glob.glob(os.path.join(DIR, '*.desktop'))

    for file_ in files:
        parser = configparser.ConfigParser()
        parser.read(file_)

        for key in parser['Desktop Entry']:
            if key.startswith('url'):
                urls.append(parser['Desktop Entry'][key])

                rename_file_if_needed(file_, parser['Desktop Entry'][key])

    urls.sort()

    return urls


def rename_file_if_needed(filename, url):
    if not 'watch?v=' in filename:
        return

    r = requests.get(url)
    t = lxml.html.fromstring(r.text)
    title = t.find(".//title").text
    title_clean = re.sub(r'[^A-Za-z0-9-_]+', '_', title)

    shutil.move(filename, os.path.join(os.path.dirname(filename), title_clean[:100] + '.desktop'))


def main():
    with open(os.path.join(DIR, 'websites.html'), 'w') as handle:
        for url in get_urls():
            handle.write('<p><a href="{url}">{url}</a></p>'.format(url=url))

if __name__ == '__main__':
    main()
