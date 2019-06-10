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

import sys, os
from subprocess import Popen, PIPE

def whereami():
    '''returns the dir where this module is installed.
    It works only if this module is imported by another module
    (see https://stackoverflow.com/a/6416114)
    so this module will never be a standalone script.
    '''
    return os.path.dirname(os.path.abspath(__file__))

def create_addargs():
    '''parses pandoc -h output and create an addargs.py module
    containing a function that adds all pandoc's arguments
    to python argparse parser
    '''
    os.chdir(whereami())
    p = Popen(['pandoc', '-v'], stdout=PIPE)
    v = p.communicate()[0]
    version = " ".join(v.splitlines()[:2])

    wpre=('def addargs_pandoc_version():\n'
          '    return "%s"\n\n'
          'def add_args(parser):\n' % version)

    wpost='\n\n'

    p = Popen(['pandoc', '-h'], stdout=PIPE)
    help = p.communicate()[0]

    rlines = help.splitlines()

    with open('addargs.py', 'w') as o:
        o.write(wpre)
        for rline in rlines:
            if rline.startswith('pandoc'):
                continue
            dirty_items = []
            for x in rline.strip().split("  "):
                dirty_items += x.split(", ")
            items = [
                dirty_item.strip()
                for dirty_item in dirty_items
                if dirty_item
            ]
            flags = []
            for item in items:
                metavar = None
                nargs = None
                action = None
                subitems = (
                    item.split("=") if item.startswith('--') else item.split()
                )
                if len(subitems) == 2:
                    if subitems[0].endswith("[")  :
                        subitems[0] = subitems[0].rstrip("[")
                        subitems[1] = subitems[1].rstrip("]")
                        nargs = '?'
                    else:
                        nargs = 1
                        action = "append"
                    metavar = subitems[1]
                elif len(subitems) == 1:
                    action = 'store_true'
                flags.append(subitems[0])

            if flags[0] == "-h": # avoid conflicts with argparse -h option
                continue
            wline = '    parser.add_argument("%s"' % '", "'.join(flags)
            if metavar:
                wline += ', metavar="%s"' % metavar
            if nargs:
                if type(nargs) is int:
                    wline += ', nargs=%s' % nargs
                else:
                    wline += ', nargs="%s"' % nargs
                    if nargs == '?':
                        wline += ', const=True'
            if action:
                wline += ', action="%s"' % action
            wline += ')\n'
            o.write(wline)

        o.write(wpost)
