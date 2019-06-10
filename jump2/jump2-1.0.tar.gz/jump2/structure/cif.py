# coding: utf-8
# Copyright (c) JUMP2 Development Team.
# Distributed under the terms of the JLU License.


#=================================================================
# This file is part of JUMP2.
#
# Copyright (C) 2017 Jilin University
#
#  Jump2 is a platform for high throughput calculation. It aims to 
#  make simple to organize and run large numbers of tasks on the 
#  superclusters and post-process the calculated results.
#  
#  Jump2 is a useful packages integrated the interfaces for ab initio 
#  programs, such as, VASP, Guassian, QE, Abinit and 
#  comprehensive workflows for automatically calculating by using 
#  simple parameters. Lots of methods to organize the structures 
#  for high throughput calculation are provided, such as alloy,
#  heterostructures, etc.The large number of data are appended in
#  the MySQL databases for further analysis by using machine 
#  learning.
#
#  Jump2 is free software. You can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published 
#  by the Free sofware Foundation, either version 3 of the License,
#  or (at your option) and later version.
# 
#  You should have recieved a copy of the GNU General Pulbic Lincense
#  along with Jump2. If not, see <https://www.gnu.org/licenses/>.
#=================================================================

"""
Module to read cif file and return a dictionary of POSCAR.

    poscar={'lattice':lattice,
            'elements':elements,
            'numbers':numbers,
            'type':type,
            'positions':positions,
           }

"""

#import numpy as np
#from spaceGroupD3 import spacegroups as SG

class SpacegroupError(Exception):
    """Base exception for the spacegroup module."""
    pass

class SpacegroupNotFoundError(SpacegroupError):
    """Raised when given space group cannot be found in data base."""
    pass

class SpacegroupValueError(SpacegroupError):
    """Raised when arguments have invalid value."""
    pass

def convert_value(value):
    """
    Convert CIF value string to corresponding python type.

    Arguments:
        value: A number string which needs to be translated to float value.

    Returns:
        value: Object of a float value.

    """
    import re
    import warnings
    value=value.strip()
    if re.match('(".*")|(\'.*\')$', value):
        return value[1:-1]
    elif re.match(r'[+-]?\d+$', value):
        return int(value)
    elif re.match(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$', value):
        return float(value)
    elif re.match(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?\(\d+\)$',
                  value):
        return float(value[:value.index('(')])  # strip off uncertainties
    elif re.match(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?\(\d+$',
                  value):
        warnings.warn('Badly formed number: "{0}"'.format(value))
        return float(value[:value.index('(')])  # strip off uncertainties
    else:
        return value


def parse_multiline_string(lines, line):
    """
    Parse semicolon-enclosed multiline string and return it.

    """
    assert line[0] == ';'
    strings = [line[1:].lstrip()]
    while True:
        line = lines.pop().strip()
        if line[:1] == ';':
            break
        strings.append(line)
    return '\n'.join(strings).strip()


def parse_singletag(lines, line):
    """
    Parse a CIF tag(entries starting with underscore). Returns
    a key-value pair.

    Arguments:
        lines: All lines.
        line: A single line starts with '_'.

    Return:
        key: The single tag(entries starting with underscore) as key.
        convert_value(value): The single value corresponded to the tag.

    Examples:
        The string '_symmetry_Int_Tables_number       62' will
        be translated to a key-value pair: {'_symmetry_Int_Tables_number': 62}.

    """
    kv = line.split(None, 1)
    if len(kv) == 1:
        key = line
        line = lines.pop().strip()
        while not line or line[0] == '#':
            line = lines.pop().strip()
        if line[0] == ';':
            value=parse_multiline_string(lines, line)
        else:
            value=line
    else:
        key, value=kv
    return key, convert_value(value)


def parse_loop(lines):
    """
    Parse a CIF loop. Returns a dict with column tag names as keys
    and a lists of the column content as values.

    Arguments:
        lines: The all lines in cif file.

    Return:
        column: A column based dictionary about the tags and
        corresponding values in a loop.

    """
    import shlex
    import warnings
    header = []
    line = lines.pop().strip()
    while line.startswith('_'):
        header.append(line.lower())
        line = lines.pop().strip()
    columns = dict([(h, []) for h in header])

    tokens = []
    while True:
        lowerline = line.lower()
        if (not line or
            line.startswith('_') or
            lowerline.startswith('data_') or
            lowerline.startswith('loop_')):
            break
        if line.startswith('#'):
            line = lines.pop().strip()
            continue
        if line.startswith(';'):
            t = [parse_multiline_string(lines, line)]
        else:
            if len(header) == 1:
                t = [line]
            else:
                t = shlex.split(line, posix=False)

        line = lines.pop().strip()

        tokens.extend(t)
        if len(tokens) < len(columns):
            continue
        if len(tokens) == len(header):
            for h, t in zip(header, tokens):
                columns[h].append(convert_value(t))
        else:
            warnings.warn('Wrong number of tokens: {0}'.format(tokens))
        tokens = []
    if line:
        lines.append(line)
    return columns


def parse_items(lines, line):
    """
    Parse a CIF data items and return a dict with all tags.

    Arguments:
        lines: The all lines in cif file.
        line: A single line which will be translated to a key-value pair
        or just be a single tag.

    Return:
        tags: The all key-value pairs obtained from parse_singletag
        and parse_loop.

    """
    tags = {}
    while True:
        if not lines:
            break
        line = lines.pop()
        if not line:
            break
        line = line.strip()
        lowerline = line.lower()
        if not line or line.startswith('#'):
            continue
        elif line.startswith('_'):
            key, value = parse_singletag(lines, line)
            tags[key.lower()] = value
        elif lowerline.startswith('loop_'):
            tags.update(parse_loop(lines))
        elif lowerline.startswith('data_'):
            if line:
                lines.append(line)
            break
        elif line.startswith(';'):
            parse_multiline_string(lines, line)
        else:
            raise ValueError('Unexpected CIF file entry: "{0}"'.format(line))
    return tags


def parse_block(lines, line):
    """
    Parse a CIF data block and return a tuple with the block name
    and a dict with all tags.

    Arguments:
        lines: The all lines in cif file.
        line: A single line which will be a single tag.

    Return:
        blockname: The name of a block which starts with 'data_'.
        tags: The all tags.

    """
    assert line.lower().startswith('data_')
    blockname = line.split('_', 1)[1].rstrip()
    tags = parse_items(lines, line)
    return blockname, tags


def parse_cif(fileobj):
    """
    Parse a CIF file. Returns a list of blockname and tag pairs.
    All tag names are converted to lower case.

    Arguments:
        fileobj: The cif file name.

    Return:
        blocks:The all blocks obtained from parse_block. (The number
        of the blocks is usually 2)

    """
    if isinstance(fileobj, basestring):
        fileobj = open(fileobj)
    lines = [''] + fileobj.readlines()[::-1]  # all lines (reversed)
    blocks = []
    while True:
        if not lines:
            break
        line = lines.pop()
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        blocks.append(parse_block(lines, line))
    return blocks

def format_symbol(symbol):
    """
    Returns well formatted Hermann-Mauguin symbol as extected by
    the database, by correcting the case and adding missing or
    removing duplicated spaces.

    """
    fixed = []
    s = symbol.strip()
    s = s[0].upper() + s[1:].lower()
    for c in s:
        if c.isalpha():
            if len(fixed) and fixed[-1] == '/':
                fixed.append(c)
            else:
                fixed.append(' ' + c + ' ')
        elif c.isspace():
            fixed.append(' ')
        elif c.isdigit():
            fixed.append(c)
        elif c == '-':
            fixed.append(' ' + c)
        elif c == '/':
            fixed.append(c)
    s = ''.join(fixed).strip()
    return ' '.join(s.split())

def equival_pos(equival, ci):
    """
    Translate the initial position coordinates to
    symmetry equivalent position coordinates.

    Arguments:
        equival: The tag (no, symbolHM or  sitesym)corresponding to
        symmetry operations.
        ci: The cif file resource.

    Return:
        symXYZ: A list contains the equivalent position coordinates.

    """

    allXYZ = []
    symXYZ = []
    for X, Y, Z in zip(ci['_atom_site_fract_x'],
                       ci['_atom_site_fract_y'],
                       ci['_atom_site_fract_z']):
        atomX = float(X)
        atomY = float(Y)
        atomZ = float(Z)

        for operation in equival:
            temp = operation.split(',')

            XX = temp[0].replace('1/2', '1./2.').replace('1/4', '1./4.')
            XX = XX.replace('3/4', '3./4.').replace('1/', '1./6.')
            XX = XX.replace('1/3', '1./3.').replace('2/3', '2./3.')
            XXX = XX.replace('5/6', '5./6.')

            YY = temp[1].replace('1/2', '1./2.').replace('1/4', '1./4.')
            YY = YY.replace('3/4', '3./4.').replace('1/6', '1./6.')
            YY = YY.replace('1/3', '1./3.').replace('2/3', '2./3.')
            YYY = YY.replace('5/6', '5./6.')

            ZZ = temp[2].replace('1/2', '1./2.').replace('1/4', '1./4.')
            ZZ = ZZ.replace('3/4', '3./4.').replace('1/6', '1./6.')
            ZZ = ZZ.replace('1/3', '1./3.').replace('2/3', '2./3.')
            ZZZ = ZZ.replace('5/6', '5./6.')

            x = atomX
            y = atomY
            z = atomZ

            XXXX = eval(XXX)
            YYYY = eval(YYY)
            ZZZZ = eval(ZZZ)

            if XXXX < 0:
                XXXX = 1.0 + XXXX

            if YYYY < 0:
                YYYY = 1.0 + YYYY

            if ZZZZ < 0:
                ZZZZ = 1.0 + ZZZZ

            if XXXX >= 1.0:
                XXXX = XXXX - 1.0

            if YYYY >= 1.0:
                YYYY = YYYY - 1.0

            if ZZZZ >= 1.0:
                ZZZZ = ZZZZ - 1.0

            atomL = [XXXX, YYYY, ZZZZ]
            allXYZ.append(atomL)

    for i in allXYZ:
        if not i in symXYZ:
            symXYZ.append(i)

    return  symXYZ

def numbers_cal(equival, ci):
    """
    Calculate the number of atoms of each type.

    Arguments:
        equival: The tag (no, symbolHM or  sitesym)corresponding to
        symmetry operations.
        ci: The cif file resource.

    Return:
        numbers: The number of atoms of each type.

    """
    numXYZ = []
    atomN = []
    numbers = []

    for X, Y, Z in zip(ci['_atom_site_fract_x'],
                       ci['_atom_site_fract_y'],
                       ci['_atom_site_fract_z']):
        atomX = float(X)
        atomY = float(Y)
        atomZ = float(Z)

        for operation in equival:
            temp = operation.split(',')

            XX = temp[0].replace('1/2', '1./2.').replace('1/4', '1./4.')
            XX = XX.replace('3/4', '3./4.').replace('1/', '1./6.')
            XX = XX.replace('1/3', '1./3.').replace('2/3', '2./3.')
            XXX = XX.replace('5/6', '5./6.')

            YY = temp[1].replace('1/2', '1./2.').replace('1/4', '1./4.')
            YY = YY.replace('3/4', '3./4.').replace('1/6', '1./6.')
            YY = YY.replace('1/3', '1./3.').replace('2/3', '2./3.')
            YYY = YY.replace('5/6', '5./6.')

            ZZ = temp[2].replace('1/2', '1./2.').replace('1/4', '1./4.')
            ZZ = ZZ.replace('3/4', '3./4.').replace('1/6', '1./6.')
            ZZ = ZZ.replace('1/3', '1./3.').replace('2/3', '2./3.')
            ZZZ = ZZ.replace('5/6', '5./6.')

            x = atomX
            y = atomY
            z = atomZ

            XXXX = eval(XXX)
            YYYY = eval(YYY)
            ZZZZ = eval(ZZZ)

            if XXXX < 0:
                XXXX = 1.0 + XXXX

            if YYYY < 0:
                YYYY = 1.0 + YYYY

            if ZZZZ < 0:
                ZZZZ = 1.0 + ZZZZ

            if XXXX >= 1.0:
                XXXX = XXXX - 1.0

            if YYYY >= 1.0:
                YYYY = YYYY - 1.0

            if ZZZZ >= 1.0:
                ZZZZ = ZZZZ - 1.0

            atomL = [XXXX, YYYY, ZZZZ]
            numXYZ.append(atomL)

        # calculate the number of atoms of each type.
        for i in numXYZ:
            if not i in atomN:
                atomN.append(i)
        temp = len(atomN)
        numbers.append(temp)
        numXYZ = []
        atomN = []

    return numbers

def lattice_vector(a, b, c, alpha, beta, gamma):
    """
    Translate lattice parameters to lattice vector.

    Arguments:
        a: The module of lattice parameter a.
        b: The module of lattice parameter b.
        c: The module of lattice parameter c.
        alpha: The included angle between vector b and c.
        beta: The included angle between vector a and c.
        gamma: The included angle between vector a and b.

    Return:
        latticeV: A list about lattice vector expressed by direct coordinate.

    """

    import math
    ax = a
    ay = 0.
    az = 0.
    bx = b * math.cos(gamma)
    by = b * math.sin(gamma)
    bz = 0.
    cx = c * math.cos(beta)
    cy = c * ((math.cos(alpha) - math.cos(beta) * math.cos(gamma)) / math.sin(gamma))
    cz = c * (math.pow(1 + 2 * math.cos(alpha) * math.cos(beta) * math.cos(gamma)
                        - math.pow(math.cos(alpha), 2) - math.pow(math.cos(beta), 2)
                        - math.pow(math.cos(gamma), 2), 0.5) / math.sin(gamma))
    latticeV = [[ax, ay, az],
                [bx, by, bz],
                [cx, cy, cz]]

    return latticeV
