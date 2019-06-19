# -*- coding: utf-8 -*-
# Copyright (c) 2016-2017, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import scipy.io as sio
import tempfile
import sys
import os
import subprocess
import numpy as np
from collections import OrderedDict
from sympathy.api import table
from sympathy.api.exceptions import SyDataError, NoDataError, SyNodeError
from sympathy.api.nodeconfig import settings


def validate(data):
    if data is None:
        raise NoDataError
    elif 'col' not in data:
        raise SyDataError("MAT file doesn't contain needed key col")
    elif 'names'not in data:
        raise SyDataError("MAT file doesn't contain needed key names")


def read_matfile_to_table(matfile):
    out_table = table.File()
    try:
        data = sio.loadmat(matfile)
        validate(data)
    except SyDataError as e:
        raise SyDataError(e.args[0] + ' in file: ' + matfile)
    except NoDataError as e:
        raise NoDataError(e.message + ' in file: ' + matfile)
    except ValueError as e:
        raise ValueError(e.message + ' in file: ' + matfile)

    column_length = len(data['col'])
    names = data['names']

    try:
        if len(data['name']):
            out_table.set_name(data['name'][0])
    except KeyError:
        pass

    if not column_length:
        return out_table
    if not len(names):
        names = [str(i) for i in range(column_length)]

    col_attr = data['col_attr']
    col_attr_values = data['col_attr_values']
    if len(col_attr):
        col_attr = col_attr[0]
    if len(col_attr_values):
        col_attr_values = col_attr_values[0]

    for i, column in enumerate(names):
        column = column.rstrip()
        output = data['col'][i]
        out_table.set_column_from_array(column, output)
        if len(col_attr):
            col_attrs = {}
            for j in range(0, len(col_attr[i])):
                if len(col_attr_values[i]):
                    value = col_attr_values[i][j]
                    col_attrs[col_attr[i][j]] = value
            out_table.set_column_attributes(column, col_attrs)

    if len(data['table_attr']):
        attributes, values = data['table_attr'].T
        attributes = [val[0] for val in attributes]
        values = [val[0] for val in values]
        out_table.set_table_attributes(dict(zip(attributes, values)))

    return out_table


def write_table_to_matfile(in_table, mat_file, header=True):
    """Write table content in table to matlab .mat file mat_file. Writes header
    to file if header is True, default=True
    """
    with open(mat_file, 'w+b') as in_file:
        names = in_table.column_names()
        if in_table is not None:
            data = OrderedDict([
                ('names', []),
                ('col', []),
                ('table_attr', []),
                ('col_attr', []),
                ('col_attr_values', []),
                ('name', '')])

            if in_table.get_name() is not None:
                data['name'] = in_table.get_name()
            table_attr = in_table.get_table_attributes()
            data['table_attr'] = np.column_stack((
                list(table_attr.keys()),
                list(table_attr.values()))).astype(np.object)

            for i, col in enumerate(names):
                if header:
                    data['names'].append(col)
                col_attr = in_table.get_column_attributes(col)
                attrs = []
                values = []
                for attr in col_attr:
                    attrs.append(attr.encode('utf-8'))
                    values.append(col_attr[attr])
                data['col_attr'].append(attrs)
                data['col_attr_values'].append(values)
                data['col'].append(in_table.get_column_to_array(col))

            data['col_attr'] = np.array(data['col_attr']).astype(np.object)
            data['col_attr_values'] = np.array(
                data['col_attr_values']).astype(np.object)

            sio.savemat(in_file, data)


def allocate_mat_file():
    # Create a new temporary .mat file to ensure that all links are resolved.
    matlab = tempfile.NamedTemporaryFile(
        prefix='matlab_',
        suffix='.mat',
        delete=False,
        dir=settings()['session_folder'])
    mat_file = matlab.name
    matlab.close()
    return mat_file


def execute_matlab(code):
    """Run matlab and copy the results."""
    code = "addpath('{}/Matlab');{}".format(
        os.environ['SY_APPLICATION_DIR'], code)
    command = ['-nodesktop', '-nosplash']
    if sys.platform == 'win32':
        command.extend(['-wait'])
    if settings()['MATLAB/matlab_jvm']:
        command.extend(['-nodisplay', '-nojvm'])
    command.extend(['-r', code])

    p_open = None
    try:
        p_open = subprocess.Popen(
            [settings()['MATLAB/matlab_path']] + command,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            stdin=subprocess.PIPE)
        p_open.wait()
    except:
        if p_open:
            p_open.kill()
        raise SyNodeError(
            'MATLAB could not be run. Have you set the MATLAB path in '
            'File/Preferences?')
    if p_open.returncode != 0:
            raise SyNodeError('MATLAB returned a non-zero exit code.')
