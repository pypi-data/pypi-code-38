# Copyright © 2018-2019 Roel van der Goot
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
"""Module jsonapi/conversions deals with JSON API conversions."""

import re
from uuid import UUID

RE_PASCAL_TO_SNAKE_1 = re.compile('(.)([A-Z][a-z]+)')
RE_PASCAL_TO_SNAKE_2 = re.compile('([a-z0-9])([A-Z])')


def uuid_name_to_number(uuid_name):
    """Converts uuid name to number."""
    return UUID(uuid_name)


def id_name_to_number(id_name):
    """Converts id name to number."""
    if '-' in id_name:
        return uuid_name_to_number(id_name)
    return UUID(int=int(id_name))


def id_number_to_name(id_number):
    """Converts id number to name."""
    if id_number.int <= 0xffffffffffff:
        return str(id_number.int)
    return str(id_number)


def pascal_to_snake(name):
    """Converts class name to url name."""

    temp = RE_PASCAL_TO_SNAKE_1.sub(r'\1_\2', name)
    return RE_PASCAL_TO_SNAKE_2.sub(r'\1_\2', temp).lower()
