#!/usr/bin/env python

"""Yaml file loader"""

import os
import yaml


class YamlLoader:
    """Load yaml files."""

    def __init__(self, filename=None):
        self._filename = filename
        self._load()

    def _load(self):
        if not os.path.isfile(self._filename):
            raise AttributeError('Unable to read: %s' % self._filename)
        try:
            with open(self._filename) as f:
                self.data = yaml.safe_load(f.read())
        except:
            raise AttributeError('%s is not a valid yaml file' % self._filename)
