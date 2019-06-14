#!/usr/bin/env python
import json
import os

import wikitextparser as wtp

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
SPELL_FILE = os.path.join(os.path.abspath(os.path.join(os.path.dirname(
    os.path.realpath(__file__)), os.pardir)), 'data', 'raw', 'all_spells.json')

all_spells = set()

for class_name in CLASSES:
    file_name = os.path.join(DATA_DIR, class_name)
    print("Parsing {}".format(class_name))
    with open(file_name, 'r') as class_file:
        parsed = wtp.parse(class_file.read())
    for template in parsed.templates:
        if template.normal_name() != 'SpellRow':
            continue
        name_arg = template.get_arg('name')
        all_spells.add(name_arg.value.strip())

sorted_spells = sorted(all_spells)
with open(SPELL_FILE, 'w') as spell_file:
    json.dump(sorted_spells, spell_file, indent=2)
