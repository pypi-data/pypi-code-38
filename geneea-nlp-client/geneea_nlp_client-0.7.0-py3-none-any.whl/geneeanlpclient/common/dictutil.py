# Copyright 2019 Geneea Analytics s.r.o.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Functions for working with nested dictionaries, mostly json-based dictionaries.
"""

from typing import Dict, Iterable, Any, Optional, Collection

JsonType = Dict[str, Any]


class DictBuilder:
    """
    A simple builder of json-like dictionaries, supporting omitting missing values and adding id references.
    """

    def __init__(self, d: JsonType) -> None:
        self.d = d

    def addIfNotNone(self, key: str, value: Optional[Any], allowEmpty: bool = False) -> 'DictBuilder':
        """
        If the value is is not None and possibly non-empty, adds it to the builder.

        :param key: key to assigne the value to
        :param value: value to be added; all values must not be None; empty collections are added depending on the allowEmpty param
        :param allowEmpty: empty collections (including strings) are not added unless this parameter is true
        """
        if isinstance(value, Collection):
            if value or (value is not None and allowEmpty):
                self.d[key] = value
        else:
            if value is not None:
                self.d[key] = value
        return self

    def addId(self, key: str, value: Optional[Any]) -> 'DictBuilder':
        """
        If the value is is not None, adds its id to the builder.

        :param key: key to assign the id of value
        :param value: value to be added if bool(value) is true, must have the id field
        """
        if value:
            self.d[key] = value.id
        return self

    def addIds(self, key: str, values: Optional[Iterable[Any]], allowEmpty: bool = False) -> 'DictBuilder':
        """
        If the values collection is is not None, adds ids of its elements to the json.

        :param key: key to assign the list of ids of values
        :param values: iterable to be added; elements must have the id field
        :param allowEmpty: empty collections are not added unless this parameter is true
        """
        if values is not None and (allowEmpty or values):
            self.d[key] = [value.id for value in values]
        return self

    def __setitem__(self, key, item) -> 'DictBuilder':
        self.d[key] = item
        return self

    def __getitem__(self, key):
        return self.d[key]

    def build(self):
        """
        Returns a dictionary in created by the builder.
        Note that repeated calls to build return the same instance.
        """
        return self.d


def getValue(obj: Optional[JsonType], key: str, default: Any = None) -> Any:
    """
    Gets a value from a json-like dictionary associated with the key. Use a dot character for separating
    each nested dictionary that needs to be traversed.

    :param obj: the mapping object
    :param key: the nested key
    :param default: a value that will be returned if the nested key does not exist or its value is None
    :return: the value associated with the nested key or the default value
    """
    if obj is None:
        return default

    d = obj
    for k in key.split('.'):
        d = d.get(k) if isinstance(d, Dict) else None
        if d is None:
            return default

    return d


