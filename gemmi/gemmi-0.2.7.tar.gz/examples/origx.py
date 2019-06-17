#!/usr/bin/env python
from __future__ import print_function
from gemmi import cif
from util import get_file_paths_from_args

for path in get_file_paths_from_args():
    block = cif.read(path).sole_block()
    origx = block.find('_database_PDB_matrix.origx',
                       ['[1][1]', '[1][2]', '[1][3]',
                        '[2][1]', '[2][2]', '[2][3]',
                        '[3][1]', '[3][2]', '[3][3]',
                        '_vector[1]', '_vector[2]', '_vector[3]'])
    if not origx:
        continue
    assert len(origx) < 2
    try:
        nums = [float(x) for x in origx[0]]
        if nums != [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0]:
            print(block.name, nums)
    except ValueError as e:
        print(block.name, e)
