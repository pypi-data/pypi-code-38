# -*- coding: utf-8 -*-
# Python version: 3
#
# Django Dataset Code Loader class
# Simon Fraser University
# Ruoyi Wang, Jetic Gū
#
# For loading the intent as a sequence of tokens
import json
import os
import sys


class Intent:
    def __init__(self, tokens):
        self.value = tokens

    def __iter__(self):
        return iter(self.value)

    def __len__(self):
        return len(self.value)

    def __repr__(self):
        return "<Intent: " + str(self.value) + ">"

    def __getitem__(self, key):
        return self.value[key]

    def export(self):
        return " ".join(self.value)


def load(file, linesToLoad=sys.maxsize):
    with open(os.path.expanduser(file)) as f:
        content = [line.strip() for line in f][:linesToLoad]
    result = []
    for line in content:
        entry = json.loads(line)
        result.append(Intent(entry))
    return result


if __name__ == '__main__':
    loaded = load(
        '/Users/ruoyi/Projects/PycharmProjects/data_fixer/bash/test.nl.filtered.tokens')
