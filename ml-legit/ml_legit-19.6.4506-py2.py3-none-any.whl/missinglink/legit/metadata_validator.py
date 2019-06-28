# -*- coding: utf-8 -*-
import six
import collections
import re


class MetadataValidator(object):

    DUPLICATE_KEY_ERROR = 'More than one field with same name in different casing is not allowed: "{}"'
    WHITESPACE_ERROR = 'Whitespaces in field names are not allowed: "{}"'

    def __init__(self, metadata_schema):
        self._metadata_schema = metadata_schema
        self._errors = []
        self._lower_keys = collections.defaultdict(list)

    def _validate_duplicate_keys(self):
        for key in self._metadata_schema.keys():
            if isinstance(key, six.string_types):
                self._lower_keys[key.lower()].append(key)

        for lower_key, keys in self._lower_keys.items():
            if len(keys) > 1:
                error = self.DUPLICATE_KEY_ERROR.format('","'.join(sorted(keys)))
                self._errors.append(error)

    def _validate_space_in_keys(self):
        pattern = re.compile('\\s')
        for key in self._metadata_schema.keys():
            if pattern.search(key):
                error = self.WHITESPACE_ERROR.format(key)
                self._errors.append(error)

    def get_validation_errors(self):
        self._validate_duplicate_keys()
        self._validate_space_in_keys()
        return self._errors
