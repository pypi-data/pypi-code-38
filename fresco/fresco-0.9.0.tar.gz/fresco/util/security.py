# Copyright 2015 Oliver Cope
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#
"""
Security-related utilities
"""
from __future__ import absolute_import


def check_equal_constant_time(a, b):
    """
    Return ``True`` if string ``a`` is equal to string ``b``.

    If ``a`` and ``b`` are of the same length, this function will take the same
    amount of time to execute, regardless of whether or not a and b are equal.
    """
    if len(a) != len(b):
        return False
    result = 0
    for c1, c2 in zip(a, b):
        result |= ord(c1) ^ ord(c2)
    return result == 0
