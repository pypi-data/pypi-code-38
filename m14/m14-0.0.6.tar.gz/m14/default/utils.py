#!/usr/bin/env python3
# !/usr/bin/env python3
# coding: utf-8


import os.path
import re
import time

import yaml


def tindex(sequence, period, count=None):
    n = len(sequence)
    idx = int(time.time() / period)
    if not count:
        return sequence[idx % n]
    count = min(n, count)
    idx = idx * count
    return [sequence[i % n] for i in range(idx, idx + count)]


def load_standard_contextmap(path, extra_path):
    ctxmap = yaml.load(open(path))
    extra = {}
    for key, val in ctxmap.items():
        if not isinstance(val, str):
            continue
        if re.match(r'\.\w+', val):
            val = key + val
        p = os.path.join(extra_path, val)
        extra[key] = yaml.load(open(p))
    ctxmap.update(extra)
    return ctxmap
