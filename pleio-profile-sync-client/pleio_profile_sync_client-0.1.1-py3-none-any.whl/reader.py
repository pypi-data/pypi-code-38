#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import OrderedDict
import csv

REQUIRED_FIELDS = ['name', 'email']
OPTIONAL_FIELDS = ['avatar']
CONVERT_DICTS = ['profile']


# UserDictReader reads fields prefixed as profile.x as a nested dict
class UserDictReader(csv.DictReader):
    def __next__(self):
        result = super().__next__()

        constructed_dict = {}

        for field in REQUIRED_FIELDS:
            constructed_dict[field] = result[field]

        for field in OPTIONAL_FIELDS:
            constructed_dict[field] = result.get(field)

        for field in CONVERT_DICTS:
            field_name = '{}.'.format(field)
            constructed_dict[field] = { key[len(field_name):] : value if value else None for (key, value) in result.items() if key.startswith(field_name) }

        return constructed_dict
