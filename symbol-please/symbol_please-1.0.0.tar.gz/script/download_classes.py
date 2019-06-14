#!/usr/bin/env python
import os
import shutil
import sys
import time
import urllib.request

import click

ENDPOINT = 'https://wiki.project1999.com/{}?action=raw'
CLASSES = [
    'Enchanter',
    'Magician',
    'Necromancer',
    'Wizard',
    'Cleric',
    'Druid',
    'Shaman',
    'Bard',
    'Monk',
    'Ranger',
    'Rogue',
    'Paladin',
    'Shadow_Knight',
    'Warrior',
]

# Get the /data/raw/class directory
DATA_DIR = os.path.join(os.path.abspath(os.path.join(os.path.dirname(
    os.path.realpath(__file__)), os.pardir)), 'data', 'raw', 'class')

if not click.confirm(
        "Redownload wiki data from Project1999 servers?"
        " This isn't necessary unless the locally committed data"
        " is out of date.", default=False):
    sys.exit(1)

for class_name in CLASSES:
    url = ENDPOINT.format(class_name)
    file_name = os.path.join(DATA_DIR, class_name)
    print("Downloading {} from {} to file {}".format(
        class_name, url, file_name))
    # Download the file from `url` and save it locally under `file_name`:
    with urllib.request.urlopen(url) as resp, open(file_name, 'wb') as out:
        shutil.copyfileobj(resp, out)

    # Spread out our requests to the server so we're no hammering it.
    time.sleep(1)
