# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
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
Some helper function to compare dictionaries and find the parts of the dict
that are different. This is mostly to help in debugging.
"""
from ..abc.serializable import Serializable
from ..helpers import config, log


def dicteq(self, other):
    """
    Compare two dicts for equality

    :param self: the first object to compare
    :param other: the oth
    :return:
    """
    if not config.debug:
        return self == other

    if self == other:
        return True

    log.debug('Differences:\n{}'.format('\n'.join(diffdict(self, other))))
    return False


def diffdict(self, other, path=None, visited=None):
    """
    Find the differences in two dictionaries.

    :param self: the first object to compare
    :param dict other: other dictionary
    :param list path: the path for nested dicts (too keep track of recursion)
    :return: list of messages indicating the differences
    :rtype: list
    """
    if path is None:
        path = []

    if visited is None:
        visited = []

    messages = []

    for k in self:
        if k not in other:
            messages.append('Key "{}" type "{}" (/{}) not found in other'.format(k,
                                                                                 type(k).__name__,
                                                                                 '/'.join(path)))

    for k in other:
        if k not in self:
            messages.append('Key "{}" type "{}" (/{}) not found in self'.format(k,
                                                                                type(k).__name__,
                                                                                '/'.join(path)))
        else:
            if self[k] != other[k]:
                if not isinstance(self[k], type(other[k])):
                    messages.append('Values for "{}" (/{}) have different type ({} vs {})'.format(k,
                                                                                                  '/'.join(path),
                                                                                                  type(self[k]).__name__,
                                                                                                  type(other[k]).__name__))
                elif isinstance(self[k], dict):
                    messages.extend(diffdict(self[k], other[k], path + [k], visited=visited))
                elif isinstance(self[k], Serializable):
                    messages.extend(diffobj(self[k], other[k], path + [k], visited=visited))
                else:
                    messages.append('Values for "{}" (/{}) differ ({} vs {})'.format(k,
                                                                                     '/'.join(path),
                                                                                     self[k],
                                                                                     other[k]))

    return messages


def diffobj(self, other, path=None, visited=None):
    """
    Compare two objects by comparing their __dict__ entries

    :param self: the first object to compare
    :param other: other objects to compare
    :param list path: the path for nested dicts (too keep track of recursion)
    :return: list of messages
    :rtype: list
    """
    if not isinstance(self, type(other)):
        return ['The types of the object do not match!']

    if visited is None:
        visited = []

    if (id(self), id(other)) not in visited:
        visited.append((id(self), id(other)))
        return diffdict(vars(self), vars(other), path=path, visited=visited)
    else:
        return []


def diffobj_str(self, other):
    """
    Compare two objects by comparing their __dict__ entries, but returns the
    differences in a single string ready for logging.

    :param self: the first object to compare
    :param other: other object to compare to
    :return: the description of the differences
    :rtype: str
    """
    return 'Differences:\n{}'.format('\n'.join(diffobj(self, other)))
