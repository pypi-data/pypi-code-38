# coding=utf8
# Copyright (c) 2013, 2017, Combine Control Systems AB
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
"""These nodes are for common file operations:
copy, delete, rename, and remove. For many operations it is possible to use
regular expressions to create new filenames, etc.
"""
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import shutil
import re
import os

import numpy as np

from sympathy.api import node as synode
from sympathy.api import node_helper
from sympathy.api import datasource as dsrc
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, adjust
from sympathy.api.exceptions import SyDataError


def copy_file(
        filename, new_filename=None, directory=None, regex=False, pattern=None,
        replace=None, no_error=False):
    if regex:
        new_filename = re.sub(pattern, replace, filename)
    elif directory:
        new_filename = os.path.join(
            directory, os.path.basename(filename))

    if (not new_filename or
            os.path.abspath(new_filename) == os.path.abspath(filename)):
        in_filename, ext = os.path.splitext(filename)
        new_filename = in_filename + ' - Copy' + ext

    new_filename = os.path.abspath(new_filename)
    path = os.path.dirname(new_filename)
    try:
        try:
            os.makedirs(path)
        except (OSError, IOError):
            pass
        shutil.copyfile(filename, new_filename)
    except Exception:
        if no_error:
            return None
        raise
    return new_filename


def delete_file(filename, delete_folder=False, no_error=False):
    directory = os.path.dirname(filename) if delete_folder else None
    try:
        os.remove(filename)
    except Exception:
        if no_error:
            filename = None
        else:
            raise
    if directory:
        try:
            os.removedirs(directory)
        except Exception:
            pass
    return filename


def rename_file(
        filename, new_filename=None, directory=None, regex=False,
        pattern=None, replace=None, no_error=False):
    if not new_filename:
        new_filename = filename
    new_filename = os.path.join(
        os.path.dirname(filename), os.path.basename(new_filename))
    if regex:
        new_filename = re.sub(pattern, replace, filename)
    try:
        os.rename(filename, new_filename)
    except (OSError, IOError):
        if not no_error:
            raise
        return None
    return new_filename


def move_file(filename, new_filename, no_error=False):
    path = os.path.dirname(new_filename)
    try:
        os.makedirs(path)
    except (OSError, IOError):
        pass
    try:
        shutil.move(filename, new_filename)
    except (OSError, IOError):
        if no_error:
            return None
        raise
    return new_filename


def regex_only_parameters(parameters):
    parameters.set_string(
        'pattern', label='RegEx pattern',
        description=(
            'Specify the regular expression that will be used for matching'))
    parameters.set_string(
        'replace', label='Replacement string',
        description=('The string to replace the match found with the regular '
                     'expression'))
    return parameters


def regex_parameters(parameters, is_dir=False):
    parameters.set_boolean(
        'use_regex', label='RegEx',
        description='Turn on/off naming using a regular expression')
    parameters = regex_only_parameters(parameters)
    return parameters


def exception_parameter(parameters):
    parameters.set_boolean(
        'error', label='Do not raise exceptions',
        description='If a file operation fails, do not raise an exception')
    return parameters


def delete_folder_parameter(parameters):
    parameters.set_boolean(
        'delete_folder', label='Delete enclosing folder if empty',
        description=(
            'If a file that is removed is the last in that folder, '
            'the folder is removed. If this operation fails, '
            'no exception is raised.'))
    return parameters


def filename_columns(parameters):
    parameters.set_list(
        'current', label='Current filenames',
        description='The column with the current file names',
        value=[0], editor=synode.Util.combo_editor(edit=True, filter=True))
    parameters.set_list(
        'new', label='New filenames',
        description='The column with the new filenames',
        value=[0], editor=synode.Util.combo_editor(edit=True, filter=True))
    return parameters


def dir_param(parameters):
    parameters.set_string(
        'filename', label='Directory',
        editor=synode.Util.directory_editor(),
        description=('Manually enter a directory'))
    return parameters


def file_param(parameters):
    parameters.set_string(
        'filename', label='Filename',
        editor=synode.Util.savename_editor(['Any files (*)']),
        description=('Manually enter a filename, if not using a regular '
                     'expression'))
    return parameters


def regex_controllers():
    return (
        synode.controller(
            when=synode.field('use_regex', state='checked'),
            action=(
                synode.field('filename', state='disabled'),
                synode.field('pattern', state='enabled'),
                synode.field('replace', state='enabled'),
            ),
        ),
    )


def get_file_lists(node_context):
    parameters = node_context.parameters

    file_table = node_context.input['port2']
    columns = file_table.column_names()

    try:
        current_index = parameters['current'].value[0]
        new_index = parameters['new'].value[0]
        # Fix indices for old configurations
        if parameters['current'].list[0] == '':
            current_index -= 1
        if parameters['current'].list[0] == '':
            new_index -= 1

        current_filenames = file_table.get_column_to_array(
            columns[current_index])
        new_filenames = file_table.get_column_to_array(
            columns[new_index])
    except IndexError:
        return [], []
    if (current_filenames.dtype.kind not in ('U', 'S') or
       new_filenames.dtype.kind not in ('U', 'S')):
            raise SyDataError(
                'One or more of the input columns have the wrong type. '
                'They should be text.')
    return current_filenames, new_filenames


class CopyFile(synode.Node):
    """Copy a file from one directory to another. Missing directories will be
    created if possible.
    """

    name = 'Copy file'
    description = ('Copy files to another location. It is possible to name '
                   'the copies using a regular expression.')
    author = ('Alexander Busck <alexander.busck@combine.se>, '
              'Andreas Tågerud<andreas.tagerud@combine.se>')
    copyright = "(C) 2013, 2017 Combine Control Systems AB"
    version = '1.0'
    nodeid = 'org.sysess.sympathy.files.copyfile'
    icon = 'copy.svg'
    tags = Tags(Tag.Disk.File)

    inputs = Ports([Port.Datasource(
        'Datasource of file to be copied', name='port1', scheme='text')])
    outputs = Ports([Port.Datasource(
        'Datasource of copied file', name='port1', scheme='text')])

    parameters = synode.parameters()
    parameters = file_param(parameters)
    parameters = regex_parameters(parameters)
    parameters = exception_parameter(parameters)
    controllers = regex_controllers()

    def execute(self, node_context):
        parameters = node_context.parameters
        ds_in = node_context.input['port1'].decode()
        try:
            filename = ds_in['path']
        except KeyError:
            return

        new_filename = copy_file(
            filename, parameters['filename'].value, None,
            parameters['use_regex'].value, parameters['pattern'].value,
            parameters['replace'].value, parameters['error'].value)

        if new_filename:
            node_context.output['port1'].encode_path(new_filename)


class CopyFiles(synode.Node):
    """Copy multiple files from one directory to another.
    Missing directories will be created if possible.
    """

    name = 'Copy files'
    description = ('Copy files to another location. It is possible to name '
                   'the copies using a regular expression.')
    author = 'Andreas Tågerud<andreas.tagerud@combine.se>'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '1.0'
    nodeid = 'org.sysess.sympathy.files.copyfiles'
    icon = 'copy.svg'
    tags = Tags(Tag.Disk.File)

    inputs = Ports([Port.Datasources('Files to be copied', name='port1')])
    outputs = Ports([Port.Datasources('Copied files', name='port1')])

    parameters = synode.parameters()
    parameters = dir_param(parameters)
    parameters = regex_parameters(parameters)
    parameters = exception_parameter(parameters)
    controllers = regex_controllers()

    def execute(self, node_context):
        parameters = node_context.parameters

        for filename in node_context.input['port1']:
            new_filename = copy_file(
                filename.decode_path(), None, parameters['filename'].value,
                parameters['use_regex'].value, parameters['pattern'].value,
                parameters['replace'].value, parameters['error'].value)
            if new_filename:
                ds = dsrc.File()
                ds.encode_path(new_filename)
                node_context.output['port1'].append(ds)


class CopyFilesWithTable(synode.Node):
    """Copies the input file datasources, to the locations designated in the
    input Table. Relative and absolute paths can be used in the input Table.
    Missing directories will be created if possible.
    """

    name = 'Copy files with Table'
    description = 'Copy files to another location using a table with paths'
    author = 'Andreas Tågerud<andreas.tagerud@combine.se>'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '1.0'
    nodeid = 'org.sysess.sympathy.files.copyfileswithtable'
    icon = 'copy.svg'
    tags = Tags(Tag.Disk.File)

    inputs = Ports([
        Port.Datasources('Files to be copied', name='port1'),
        Port.Table('New file names', name='port2')])
    outputs = Ports([Port.Datasources('Copied files', name='port1')])

    parameters = synode.parameters()
    parameters = filename_columns(parameters)
    parameters = exception_parameter(parameters)

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['current'], node_context.input['port2'])
        adjust(node_context.parameters['new'], node_context.input['port2'])

    def execute(self, node_context):
        current_filenames, new_filenames = get_file_lists(node_context)
        for ds in node_context.input['port1']:
            abs_path = os.path.abspath(ds.decode_path())
            rel_path = os.path.relpath(abs_path)
            if abs_path in current_filenames:
                file = abs_path
            elif rel_path in current_filenames:
                file = rel_path
            else:
                continue
            new_filename = copy_file(
                file,
                new_filenames[np.where(current_filenames == file)[0][0]],
                no_error=node_context.parameters['error'].value)
            new_file = dsrc.File()
            new_file.encode_path(new_filename)
            node_context.output['port1'].append(new_file)


class CopyFilesWithDatasources(synode.Node):
    """Copies the input file datasources, to the locations designated in the
    second datasources input, element by element. Missing directories will be
    created if possible.
    """

    name = 'Copy files with Datasources'
    description = 'Copy files to another location using a table with paths'
    author = 'Andreas Tågerud<andreas.tagerud@combine.se>'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '1.0'
    nodeid = 'org.sysess.sympathy.files.copyfileswithdsrc'
    icon = 'copy.svg'
    tags = Tags(Tag.Disk.File)

    inputs = Ports([
        Port.Datasources('Files to be copied', name='port1'),
        Port.Datasources('File destinations to copy to', name='port2')])
    outputs = Ports([Port.Datasources('Copied files', name='port1')])

    parameters = synode.parameters()
    parameters = exception_parameter(parameters)

    def execute(self, node_context):
        in_dss = node_context.input['port1']
        out_dss = node_context.input['port2']

        for in_ds, out_ds in zip(in_dss, out_dss):
            new_filename = copy_file(
                in_ds.decode_path(), out_ds.decode_path(),
                no_error=node_context.parameters['error'].value)
            if new_filename:
                out_file = dsrc.File()
                out_file.encode_path(new_filename)
                node_context.output['port1'].append(out_file)


class DeleteFile(synode.Node):
    """Deletes one file."""

    name = 'Delete file'
    description = 'Delete a file'
    author = ('Magnus Sandén <magnus.sanden@combine.se>'
              'Andreas Tågerud<andreas.tagerud@combine.se>')
    copyright = "(C) 2016-2017 Combine Control Systems AB"
    version = '1.0'
    nodeid = 'org.sysess.sympathy.files.deletefile'
    icon = 'delete.svg'
    tags = Tags(Tag.Disk.File)

    inputs = Ports([Port.Datasource('File to delete', name='port1')])
    outputs = Ports([Port.Datasource('Path to deleted file', name='port1')])

    parameters = synode.parameters()
    parameters = delete_folder_parameter(parameters)
    parameters = exception_parameter(parameters)

    def execute(self, node_context):
        parameters = node_context.parameters
        filename = node_context.input['port1'].decode_path()
        if filename:
            del_file = delete_file(
                filename, parameters['delete_folder'].value,
                no_error=parameters['error'].value)
            if del_file:
                ds = dsrc.File()
                ds.encode_path(del_file)
                node_context.output['port1'].encode_path(del_file)


DeleteFiles = node_helper.list_node_factory(
    DeleteFile,
    ['port1'], ['port1'],
    name='Delete files',
    nodeid='org.sysess.sympathy.files.deletefiles')


class RenameFile(synode.Node):
    """Rename one file using a new filename."""

    name = 'Rename File'
    version = '1.0'
    author = 'Andreas Tågerud<andreas.tagerud@combine.se>'
    copyright = '(C) 2017 Combine Control Systems AB'
    icon = 'rename.svg'
    description = 'Rename file in the current directory'
    nodeid = 'org.sysess.sympathy.files.renamefile'
    tags = Tags(Tag.Disk.File)

    inputs = Ports([Port.Datasource('File to rename', name='port1')])
    outputs = Ports([Port.Datasource('Path to renamed file', name='port1')])

    parameters = synode.parameters()
    parameters = file_param(parameters)
    parameters = regex_parameters(parameters)
    parameters = exception_parameter(parameters)
    controllers = regex_controllers()

    def execute(self, node_context):
        parameters = node_context.parameters
        filename = node_context.input['port1'].decode_path()
        if filename:
            new_filename = rename_file(
                filename, parameters['filename'].value, None,
                parameters['use_regex'].value,
                parameters['pattern'].value,
                parameters['replace'].value,
                no_error=parameters['error'].value)
            if new_filename:
                node_context.output['port1'].encode_path(new_filename)


RenameFiles = node_helper.list_node_factory(
    RenameFile,
    ['port1'], ['port1'],
    name='Rename Files',
    nodeid='org.sysess.sympathy.files.renamefiles')


class RenameFilesWithTable(synode.Node):
    """Using a table with old names and new names in two columns, this node
    renames files in the same folder as the input datasources.
    The datasources can point to multiple files in different directories.
    The column with the current filenames can be an absolute or relative path,
    but the column with the new names should only contain the filename, with no
    directory prefix. If a prefix is present it will be discarded.
    """

    name = 'Rename Files with Table'
    author = 'Andreas Tågerud<andreas.tagerud@combine.se>'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '1.0'
    icon = 'rename.svg'
    description = (
        'Using a table with a a column for current filenames and one for new '
        'filenames, rename the files')
    nodeid = 'org.sysess.sympathy.files.renamefileswithtable'
    tags = Tags(Tag.Disk.File)

    inputs = Ports([
        Port.Datasources('Files to be renamed', name='port1'),
        Port.Table('List of new filenames', name='port2')])
    outputs = Ports([Port.Datasources('Renamed files', name='port1')])

    parameters = synode.parameters()
    parameters = filename_columns(parameters)
    parameters = exception_parameter(parameters)

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['current'], node_context.input['port2'])
        adjust(node_context.parameters['new'], node_context.input['port2'])

    def execute(self, node_context):
        filenames, new_filenames = get_file_lists(node_context)
        filenames = np.array([os.path.basename(file) for file in filenames])

        for ds in node_context.input['port1']:
            orig = ds.decode_path()
            directory, file = os.path.split(orig)
            if orig in filenames:
                idx = np.where(filenames == orig)[0][0]
            elif file in filenames:
                idx = np.where(filenames == file)[0][0]
            else:
                continue
            new = os.path.join(directory, os.path.basename(new_filenames[idx]))
            new = rename_file(
                orig, new, no_error=node_context.parameters['error'].value)
            new_file = dsrc.File()
            new_file.encode_path(new)
            node_context.output['port1'].append(new_file)


class MoveFile(synode.Node):
    """Move one file from one location to another."""

    name = 'Move File'
    author = 'Andreas Tågerud<andreas.tagerud@combine.se>'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '1.0'
    icon = 'move.svg'
    description = (
        'Moves a file to new location using a datasource with the location')
    nodeid = 'org.sysess.sympathy.files.movefile'
    tags = Tags(Tag.Disk.File)

    inputs = Ports([
        Port.Datasource('File to be moved', name='port1'),
        Port.Datasource('New location', name='port2')])
    outputs = Ports([Port.Datasource('Moved file', name='port1')])

    parameters = synode.parameters()
    parameters = exception_parameter(parameters)

    def execute(self, node_context):
        filename = node_context.input['port1'].decode_path()
        if filename:
            new_filename = move_file(
                filename, node_context.input['port2'].decode_path(),
                no_error=node_context.parameters['error'].value)
            if new_filename:
                node_context.output['port1'].encode_path(new_filename)


MoveFiles = node_helper.list_node_factory(
    MoveFile,
    ['port1', 'port2'], ['port1'],
    name='Move Files',
    nodeid='org.sysess.sympathy.files.movefiles')
