#!/usr/bin/env python
import os


def parse(line):
    """parse line and return a dictionary with variable value"""
    if line.lstrip().startswith('#'):
        return {}
    if not line.lstrip():
        return {}
    """find the second occurence of a quote mark:"""
    if line.find("export=") == 0:
        line = line.replace("export=", "")
    quote_delimit = max(line.find('\'', line.find('\'') + 1),
                        line.find('"', line.rfind('"')) + 1)
    """find first comment mark after second quote mark"""
    if '#' in line:
        line = line[:line.find('#', quote_delimit)]
    key, value = map(lambda x: x.strip().strip('\'').strip('"'),
                     line.split('=', 1))
    return {key: value}


path=".env"
for line in open(path).read().splitlines():
    os.environ.update(parse(line))
