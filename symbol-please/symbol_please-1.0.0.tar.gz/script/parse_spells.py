#!/usr/bin/env python
import json
import os
import re

import wikitextparser as wtp

# Get the /data/raw/spell directory
DATA_DIR = os.path.join(os.path.abspath(os.path.join(os.path.dirname(
    os.path.realpath(__file__)), os.pardir)), 'data', 'raw', 'spell')
SPELL_FILE = os.path.join(os.path.abspath(os.path.join(os.path.dirname(
    os.path.realpath(__file__)), os.pardir)), 'data', 'raw', 'all_spells.json')
DATA_FILE = os.path.join(os.path.abspath(os.path.join(os.path.dirname(
    os.path.realpath(__file__)), os.pardir)),
    'symbol_please', 'data', 'spell_data.json')

LEVEL_REGEX = re.compile(r' @L(?P<level>\d+)', re.IGNORECASE)
SECONDS_REGEX = re.compile(r'(?P<time>\d+(\.\d+)?) second(s)?', re.IGNORECASE)
TICKS_REGEX = re.compile(r'(?P<time>\d+(\.\d+)?) tick(s)?', re.IGNORECASE)
MINUTES_REGEX = re.compile(r'(?P<time>\d+(\.\d+)?) minute(s)?', re.IGNORECASE)
HOURS_REGEX = re.compile(r'(?P<time>\d+(\.\d+)?) hour(s)?', re.IGNORECASE)

spell_data = {}

# The wiki uses the incorrect names
NAME_FIXES = {
    'Improved Invis to Undead': 'Improved Invis vs Undead',
}


def parse_duration_string(duration):
    """Parse a duration string and return seconds, level."""
    seconds = 0
    level = None

    seconds_match = SECONDS_REGEX.search(duration)
    if seconds_match is not None:
        seconds += float(seconds_match.group('time'))

    ticks_match = TICKS_REGEX.search(duration)
    if ticks_match is not None:
        seconds += float(ticks_match.group('time')) * 6

    minutes_match = MINUTES_REGEX.search(duration)
    if minutes_match is not None:
        seconds += float(minutes_match.group('time')) * 60

    hours_match = HOURS_REGEX.search(duration)
    if hours_match is not None:
        seconds += float(hours_match.group('time')) * 3600

    seconds = int(seconds)

    level_match = LEVEL_REGEX.search(duration)
    if level_match is not None:
        level = int(level_match.group('level'))

    return seconds, level


with open(SPELL_FILE, 'r') as spell_file:
    all_spells = json.load(spell_file)

for spell_name in all_spells:
    file_name = os.path.join(DATA_DIR, spell_name.replace(
        "'", "").replace(":", ""))

    spell_name = NAME_FIXES.get(spell_name, spell_name)
    print("Parsing {}".format(spell_name))
    with open(file_name, 'r') as class_file:
        parsed = wtp.parse(class_file.read())

    spellpage = next(
        t for t in parsed.templates if t.normal_name() in (
            'Spellpage', 'Spellpagesmart'))

    duration = spellpage.get_arg('duration').value.strip()
    target_type = spellpage.get_arg('target_type').value.strip()
    msg_cast_on_you = spellpage.get_arg('msg_cast_on_you').value.strip()
    msg_cast_on_other = spellpage.get_arg('msg_cast_on_other').value.strip()
    msg_wears_off = spellpage.get_arg('msg_wears_off').value.strip()

    # Clean up data
    if "Instant" in duration or "Up to" in duration:
        duration = None
    elif ' to ' in duration:
        duration_parts = duration.split(" to ")
        start_seconds, start_level = parse_duration_string(duration_parts[0])
        end_seconds, end_level = parse_duration_string(duration_parts[1])
        if start_level is None or end_level is None:
            raise ValueError(
                "Error getting level from multipart duration '{}'".format(
                    duration))
        duration = {
            "start": {
                "level": start_level,
                "duration": start_seconds,
            },
            "end": {
                "level": end_level,
                "duration": end_seconds,
            },
        }
    else:
        duration, _ = parse_duration_string(duration)

    if "Group" in target_type:
        target_type = "Group"
    elif target_type in (
            "Line of Sight", "Pet", "Animal", "Summoned", "Undead", "Plant",
            "Corpse", "Lifetap", "Uber Giants", "Uber Dragons"):
        target_type = "Single"
    elif target_type in ("Targeted AE", "PB AE"):
        target_type = "AE"
    elif target_type not in ("Single", "Self"):
        raise ValueError("Unknown target type '{}'".format(target_type))

    msg_cast_on_other = msg_cast_on_other.replace(
        "Someone  ", "Someone ").replace("Someone 's", "Someone's")

    spell_data[spell_name] = {
        'name': spell_name,
        'duration': duration,
        'target_type': target_type,
        'msg_cast_on_you': msg_cast_on_you,
        'msg_cast_on_other': msg_cast_on_other,
        'msg_wears_off': msg_wears_off,
    }

with open(DATA_FILE, 'w') as data_file:
    json.dump(spell_data, data_file, indent=2)
