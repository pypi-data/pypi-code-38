# -*- coding: utf-8 -*-
from typing import List

import re

pattern_version = re.compile(r'\D*(?P<version>(?:(\d+)|)(?:\.(\d+)|)(?:\.(\d+)|)(?:\.(\d+)|))\D*')


def get_version_as_number(version: str) -> int:
    result = 0
    m = 10000
    match = pattern_version.match(version)
    if match is not None:
        a = match.group(2)
        a = '0' if a is None else a
        b = match.group(3)
        b = '0' if b is None else b
        c = match.group(4)
        c = '0' if c is None else c
        d = match.group(5)
        d = '0' if d is None else d
        result = int(a) * m ** 3 + int(b) * m ** 2 + int(c) * m + int(d)
    return result


def get_version_as_parts(version: str) -> List[str]:
    result = []
    match = pattern_version.match(version)
    if match is not None:
        a = match.group(2)
        if a is not None:
            result.append(a)
        b = match.group(3)
        if b is not None:
            result.append(b)
        c = match.group(4)
        if c is not None:
            result.append(c)
        d = match.group(5)
        if d is not None:
            result.append(d)
    return result
