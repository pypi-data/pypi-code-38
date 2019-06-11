#!/usr/bin/env python3
'''
generate_python_file_lists.py
==============================

:Author: |author_names|
:Release: |version|
:Date: |today|


Purpose
=======

Helper functions for tests for project_quickstart

Recursively searches directories and saves results to files

Ran by
generate_ref_files.sh
in order to generate reference files to test against.

Used as a way to substitute for ls -Ra1 dir > dir.tree
'''
import os

test_name = 'pq_test_ref'

dirs = ['{}'.format(test_name),
        'pipeline_{}'.format(test_name),
        'pq_example',  # this is fixed for --example
        ]

# Only writes out file names, not base path, so if location changes it won't be checked:
for d in dirs:
    name = str(str(d) + '.py_tree')
    name = open(name, 'w')
    d_list = []
    for dirpath, dirnames, filenames in os.walk(d):
        for f in filenames:
            d_list.append(f)
    d_list.sort()
    name.write('\n'.join(d_list))
    name.close()

quit()
