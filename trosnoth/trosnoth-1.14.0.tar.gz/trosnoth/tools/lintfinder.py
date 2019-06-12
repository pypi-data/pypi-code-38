# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2017 Joshua D Bartlett
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

import heapq
import os
import re
import subprocess
import sys

EXCLUDE_DIRS = {['test']}
POOR_FUNCTION_RE = re.compile('\s*def [A-Z]')
IMPORT_COIN_RE = re.compile('from .+ import \*')

THIS_FILE = os.path.abspath(__file__)


def main():
    if len(sys.argv) > 2:
        print('Expected one arg only.')
        sys.exit(1)

    if len(sys.argv) == 2:
        path = sys.argv[1]
        if os.path.isfile(path):
            analyseFile(path)
            return
    else:
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    results = []
    for base, dirs, files in os.walk(path):
        dirs[:] = [
            d for d in dirs if not d.startswith('.') and d not in EXCLUDE_DIRS]
        for f in files:
            if f.endswith('.py'):
                filename = os.path.join(base, f)
                s = score(filename)
                if s:
                    heapq.heappush(results, (-s, filename))

    for i in range(20):
        if len(results) == 0:
            print('--- no more bad files ---')
            break
        print(('%d: %s' % heapq.heappop(results)))


def score(filename):
    if filename == THIS_FILE:
        return 0

    contents = [
        l for l in open(filename, 'rb').read().splitlines()
        if 'pragma: noqa' not in l]
    return (
        longLineCount(contents) +
        printCount(contents) +
        trailingWhitespaceCount(contents) +
        trailingBackslashCount(contents) +
        5 * tabCount(contents) +
        3 * pyflakesScore(filename) +
        2 * todoCount(contents) +
        2 * poorlyNamedFunctionCount(contents) +
        (25 if containsImportStar(contents) else 0)
    )


def analyseFile(filename):
    contents = [
        l for l in open(filename, 'rb').read().splitlines()
        if 'pragma: noqa' not in l]
    print(('Long lines: %d' % (longLineCount(contents),)))
    print(('prints: %d' % (printCount(contents),)))
    print(('trailing whitespaces: %d' % (trailingWhitespaceCount(contents),)))
    print(('trailing backslashes: %d' % (trailingBackslashCount(contents),)))
    print(('tabs: %d' % (tabCount(contents),)))
    print(('pyflakes score: %d' % (pyflakesScore(filename),)))
    print(('TODO lines: %d' % (todoCount(contents),)))
    print(('poorly named functions: %d' % (poorlyNamedFunctionCount(contents),)))
    print(('contains import *: %r' % (containsImportStar(contents),)))


def longLineCount(contents):
    '''
    Returns the number of lines in the file which are longer than 80 characters
    wide.
    '''
    return sum([1 if len(l) > 80 else 0 for l in contents])


def trailingBackslashCount(contents):
    '''
    Returns the number of lines in the file which are longer than 80 characters
    wide.
    '''
    return sum([1 if l.rstrip().endswith('\\') else 0 for l in contents])


def tabCount(contents):
    '''
    Returns the number of lines in the file which contain tabs.
    '''
    return sum([1 if '\t' in l else 0 for l in contents])


def printCount(contents):
    '''
    Returns the number of print statements apparently in the code.
    '''
    return sum([1 if l.lstrip().startswith('print ') else 0 for l in contents])


def todoCount(contents):
    '''
    Returns the number of lines which contain TODO, FIXME or XXX.
    '''
    return sum([
        1 if ('TODO' in l or 'FIXME' in l or 'XXX' in l) else 0
        for l in contents])


def poorlyNamedFunctionCount(contents):
    '''
    Returns the number of functions with capitalised names.
    '''
    return sum([1 if POOR_FUNCTION_RE.match(l) else 0 for l in contents])


def trailingWhitespaceCount(contents):
    '''
    Returns the number of lines in the file which have trailing whitespace.
    '''
    return sum([1 if l.rstrip() != l else 0 for l in contents])


def containsImportStar(contents):
    '''
    Returns True or False depending on whether the file contains import *.
    '''
    return any(IMPORT_COIN_RE.match(l) for l in contents)


def pyflakesScore(filename):
    cmd = ['pyflakes', filename]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.communicate()
    return p.returncode


if __name__ == '__main__':
    main()
