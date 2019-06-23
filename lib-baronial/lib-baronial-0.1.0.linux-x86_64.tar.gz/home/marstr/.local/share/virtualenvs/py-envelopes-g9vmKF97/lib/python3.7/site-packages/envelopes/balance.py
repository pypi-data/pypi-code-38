# Copyright 2019 Martin Strobel
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

import re
import decimal

TERM_PATTERN = re.compile(r'^\s*(?P<id>[^\s\-\d]+?)??\s*(?P<magnitude>-?(?:[\d]*|(?:\d{1,3}(?:,\d{3})+))(?:\.\d+)?)$')


class Balance(dict):
    """ Holds a collection of assets, and the corresponding magnitudes present.
    """

    def __init__(self, value="0"):
        chunks = value.split(';')
        for chunk in chunks:
            parsed = TERM_PATTERN.match(chunk)
            if parsed:
                self[parsed.group('id')] = decimal.Decimal(parsed.group('magnitude').replace(",", ""))
            else:
                raise RuntimeError('"{}" is not a valid balance'.format(value))

    def __add__(self, other):
        retval = Balance()

        unseen = set(other.keys())

        for k, v in self.items():
            retval[k] = v + other.get(k, decimal.Decimal("0"))
            unseen.discard(k)

        for k in unseen:
            retval[k] = other[k]

        return retval

    def __sub__(self, other):
        retval = Balance()

        unseen = set(other.keys())

        for k, v in self.items():
            retval[k] = v - other.get(k, decimal.Decimal("0"))
            unseen.discard(k)

        for k in unseen:
            retval[k] = -other[k]

        return retval

    def __eq__(self, other):
        unseen = set(other.keys())

        for k, v in self.items():
            unseen.discard(k)
            if v != other.get(k, decimal.Decimal("0")):
                return False

        for entry in unseen:
            if other[entry] != decimal.Decimal("0"):
                return False

        return True
