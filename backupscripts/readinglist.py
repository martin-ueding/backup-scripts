#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2014 Martin Ueding <dev@martin-ueding.de>

import configparser
import os.path
import glob

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

    urls.sort()

    return urls

def main():
    with open(os.path.join(DIR, 'websites.html'), 'w') as handle:
        for url in get_urls():
            handle.write('<p><a href="{url}">{url}</a></p>'.format(url=url))

if __name__ == '__main__':
    main()
