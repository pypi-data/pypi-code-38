"""Provides output formatting for JSON bodies, converting to columnar lists, with keyword inclusion.
"""
from __future__ import print_function

import sys
import json
from tabulate import tabulate, tabulate_formats

class Formatter:
    choices = ['json', 'json_min']
    choices.extend(tabulate_formats)
    choices.sort()

    def __init__(self, style='simple', file=sys.stdout):
        self._style = style
        self._file = file

    def display(self, objs):
        if self._style == 'json_min':
            json.dump(objs, self._file)
            return

        if self._style == 'json':
            json.dump(objs, self._file, indent=2)
            return

        if isinstance(objs, dict):
            table = [objs]
        else:
            table = {}
            for obj in objs:
                for key, val in obj.iteritems():
                    if key not in table: table[key] = []
                    table[key].append(val)

        print(tabulate(table, headers='keys', tablefmt=self._style), file=self._file)
