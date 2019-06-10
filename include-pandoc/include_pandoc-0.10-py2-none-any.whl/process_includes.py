#!/usr/bin/env python
#
#SPDX-License-Identifier: GPL-3.0-only
#
# Copyright (C) 2019 Alberto Pianon <pianon@array.eu>
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 3.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <https://www.gnu.org/licenses/>.
#
# This script processes file(s) by detecting and processing include lines in the
# following format:
# !include relative_or_absolute/path/to/file 
#
# (include statement must be put on a single line, 
# with no spaces at the beginning)
#
# It supports also nested/recursive includes.
# 
# If relative paths are used in includes, they are regarded as relative to the
# path of the 'including' file; in nested/recursive includes, relative paths
# are regarded as relative to the path of the nested 'including' file, not to
# the main/parent file path.
#
# This code can be used as a standalone script (it will process files passed
# as arguments), or as a library, by importing the process_file function.

import sys, os

def process_file(f, stdout, byte=False):
    '''recursively processes includes in file f
    'f' and 'stdout' are file objects, respectively for input and output;
    'byte' must be set to True if stdout object requires bytes objects as input 
    '''
    curdir = os.getcwd()
    if f.name == "<stdin>":
        dirname = curdir
    else:
        dirname = os.path.dirname(os.path.abspath(f.name))
        os.chdir(dirname) #needed to handle possible relative paths in includes
    line = f.readline()
    while line:
        if line.startswith("!include "):
            included_filename = line[9:].strip()
            # TODO: handle errors
            with open(included_filename, "r") as incl_f:
                process_file(incl_f, stdout)
            os.chdir(dirname) # recursively called process_file could have  
                              # changed current dir: going back to the 
                              # 'original' dir
        else:
            if byte:
                line = bytes(line)
            stdout.write(line)
        line = f.readline()
    os.chdir(curdir)

def main():
    if len(sys.argv) == 1:
        process_file(sys.stdin, sys.stdout)
    else:
        sys.argv.pop(0)
        for filename in sys.argv:
            with open(filename) as f:
                process_file(f, sys.stdout)
                
if __name__=="__main__":
    main()
