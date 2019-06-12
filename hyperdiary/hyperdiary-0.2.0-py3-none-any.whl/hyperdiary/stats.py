from sys import argv
from argparse import ArgumentParser
from collections import OrderedDict

from .diary import find_tags, find_ids, iter_entries, Diary

def stats(entries):

    output = OrderedDict()
    output['# Days'] = len(entries)
    output['# Entries'] = sum(len(v) for v in entries.values())
    output['# Taggings'] = sum(len(find_tags(l)) for d, l, t in iter_entries(entries))
    output['# Identification'] = sum(len(find_ids(l)) for d, l, t in iter_entries(entries))

    for key, val in output.items():
      print('{:.<20}{:.>5}'.format(key, val))
