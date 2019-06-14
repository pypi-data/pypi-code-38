#!/usr/bin/env python
import json
import os
import shutil
import sys
import time
import urllib.request
import urllib.parse

import click

ENDPOINT = 'https://wiki.project1999.com/{}?action=raw'

# Get the /data/raw/spell directory
DATA_DIR = os.path.join(os.path.abspath(os.path.join(os.path.dirname(
    os.path.realpath(__file__)), os.pardir)), 'data', 'raw', 'spell')
SPELL_FILE = os.path.join(os.path.abspath(os.path.join(os.path.dirname(
    os.path.realpath(__file__)), os.pardir)), 'data', 'raw', 'all_spells.json')

NEEDS_DISAMBIGUATION = {
    "Sacrifice": "Sacrifice_(spell)",
    "Shield of Thorns": "Shield_of_Thorns_(Spell)",
    "Tishan's Discord": "Tishan`s_Discord",
    "Zumaik's Animation": "Zumaik`s_Animation",
}

if not click.confirm(
        "Redownload wiki data from Project1999 servers?"
        " This isn't necessary unless the locally committed data"
        " is out of date.", default=False):
    sys.exit(1)

with open(SPELL_FILE, 'r') as spell_file:
    all_spells = json.load(spell_file)

for spell_name in all_spells:
    if spell_name in NEEDS_DISAMBIGUATION.keys():
        # Needs to be disambiguated
        spell_name_url = NEEDS_DISAMBIGUATION[spell_name]
    else:
        spell_name_url = spell_name.replace(" ", "_")

    url = ENDPOINT.format(urllib.parse.quote_plus(spell_name_url))
    file_name = os.path.join(DATA_DIR, spell_name.replace(
        "'", "").replace(":", ""))
    print("Downloading {} from {} to file {}".format(
        spell_name, url, file_name))
    # Download the file from `url` and save it locally under `file_name`:
    with urllib.request.urlopen(url) as resp, open(file_name, 'wb') as out:
        shutil.copyfileobj(resp, out)

    # Spread out our requests to the server so we're no hammering it.
    time.sleep(1)
