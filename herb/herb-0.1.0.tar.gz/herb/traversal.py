import os
from pathlib import Path

from more_itertools import unique_everseen


def traverse(root: str):
    priority = []
    priority_file = os.path.join(root, '.backup_priority')

    did_include_all = False
    if os.path.isfile(priority_file):
        with open(priority_file) as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                if line == '*':
                    did_include_all = True
                priority.extend(Path(root).glob(line))

    if not did_include_all:
        priority.extend(Path(root).glob('*'))

    to_trav = unique_everseen(priority)

    for f in to_trav:
        if os.path.islink(f):
            # we don't want to follow links, just return them untouched
            yield f
        elif os.path.isdir(f):
            for ret in traverse(f):
                yield ret
        else:
            yield f
