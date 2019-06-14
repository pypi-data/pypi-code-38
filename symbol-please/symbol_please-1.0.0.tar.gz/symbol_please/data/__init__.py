"""Spell data module for symbol_please."""
import json
import os

DATA_FILE = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'spell_data.json')

with open(DATA_FILE, 'r') as data_file:
    SPELL_DATA = json.load(data_file)
