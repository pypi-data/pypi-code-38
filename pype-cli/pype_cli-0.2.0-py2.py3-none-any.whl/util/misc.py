# -*- coding: utf-8 -*-
"""Utility functions."""

import json

from pygments import highlight
from pygments.formatters.terminal import TerminalFormatter
from pygments.lexers.data import JsonLexer


def get_from_json_or_default(json, path, default_value):
    """Try to load a key breadcrumb from a JSON object or return default."""
    if not path:
        return default_value
    json = json if json else {}
    try:
        for breadcrumb in path.split('.'):
            json = json[breadcrumb]
        return json if json else default_value
    except KeyError:
        return default_value


def beautify_json_string(json_string, colorize=False, sort_keys=False):
    """Beautify JSON string with optional coloring."""
    json_obj = json.loads(json_string)
    formatted_json = json.dumps(json_obj, sort_keys=sort_keys, indent=4)
    if not colorize:
        return formatted_json
    return highlight(formatted_json, JsonLexer(), TerminalFormatter())


def truncate_with_ellipsis(string, length):
    """Truncate a string at the given length or return it."""
    string = string if string else ''
    return (string[:length] + '..') if len(string) > length else string


def query_yes_no(question, default='yes'):
    """Ask a yes/no question via raw_input() and return their answer."""
    valid = {'yes': True, 'y': True, 'ye': True,
             'no': False, 'n': False}
    if default is None:
        prompt = ' [y/n] '
    elif default == 'yes':
        prompt = ' [Y/n] '
    elif default == 'no':
        prompt = ' [y/N] '
    else:
        raise ValueError('invalid default answer: {}'.format(default))

    while True:
        print(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            print('Please respond with "yes" or "no" (or "y" or "n").')
