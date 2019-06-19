# -*- coding: utf-8 -*-
# Copyright (c) 2013, Combine Control Systems AB
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
from collections import OrderedDict
import six
import io
import os
from sympathy.api.exceptions import sywarn

LIBRARY_INI = 'library.ini'
library_infos = {}


class LibraryInfo(object):
    def __init__(self, filename, info):
        super(LibraryInfo, self).__init__()
        self._filename = filename
        self._info = info

    def keys(self):
        """Return a dict with sections containing a list of keys in each
        section.
        """
        keys = {}
        for section in self._info.keys():
            keys[section] = list(self._info[section].keys())

        return keys

    def file_name(self):
        return self._filename

    def __contains__(self, key):
        """If key is section name only, return true if section is present.
        Else if key is (section name, property name) return true if property
        exists in section.
        """
        if isinstance(key, six.string_types):
            return key in self._info
        else:
            return key[1] in self._info[key[0]].keys()

    def __getitem__(self, key):
        """If key is section name only, return section dict if section
        is present. Else if key is (section name, property name) return
        property.
        """
        try:
            if isinstance(key, six.string_types):
                return self._info[key]
            return self._info[key[0]][key[1]]
        except KeyError:
            raise KeyError('Library info does not have key: "' + key + '"')

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __setitem__(self, key, value):
        """If key is section name only, create new section. Else if key is
        (section name, property name) create section if not present, then add
        the property to that section.
        """
        if isinstance(key, six.string_types):
            self._info[key] = OrderedDict()
        else:
            section = key[0]
            prop = key[1]
            if section in self._info:
                self._info[section][key] = value
            else:
                self._info[section] = {}
            self._info[section][prop] = value

    def sync(self):
        """Save to disk"""
        string = self._to_string()
        try:
            with io.open(self._filename, 'w', encoding='utf8') as ini:
                ini.write(string)
        except (IOError, OSError):
            sywarn('Library file ' + self._filename + ' cannot be written.')

    def _to_string(self):
        lines = []
        for key in self._info:
            lines.append('[' + key + ']')
            for section_key in self._info[key]:
                lines.append('{}={}'.format(
                    section_key, self._info[key][section_key]))
        if len(lines):
            return '\n'.join(lines) + '\n'
        else:
            return ''


def read_library_info(filename=None, directory=None):
    info = []
    ini_path = filename
    assert filename or directory
    if filename is None:
        ini_path = os.path.join(directory, LIBRARY_INI)

    try:
        with io.open(ini_path, 'r', encoding='utf8') as ini:
            line = ini.readline()
            while len(line):
                info.append(line)
                line = ini.readline()
    except (IOError, OSError):
        pass
    else:
        return LibraryInfo(ini_path, _parse_input(info))


def create_library_info(ini_path, name):
    library_info = read_library_info(ini_path)

    if library_info is None:
        sywarn('Library file ' + ini_path + ' cannot be read.')
        return False
    else:
        global library_infos
        library_infos[name] = library_info
        return True


def _parse_input(info):
    properties = OrderedDict()
    section = None
    for i, line in enumerate(info):
        if len(line):
            if line[0] == '[':
                section = line[1:].split(']')
                if len(section) > 1:
                    properties[section[0]] = OrderedDict()
                else:
                    break
                continue
            prop = line.split('=')
            if len(prop) > 1 and section is not None:
                properties[section[0]][prop[0]] = prop[1].strip()
            elif section is None:
                break
            else:
                sywarn(
                    'File not correctly formatted on line ' +
                    str(i) + '.\n'
                    'Each section in library.ini should be on the form:\n'
                    '[Section]\n'
                    'Property1=property1\n'
                    'Property2=property2\n'
                    'etc.')
    return properties


def remove_library(name):
    if name in library_infos:
        del library_infos[name]


def sync():
    for key in library_infos.keys():
        library_infos[key].sync()


def instance():
    return library_infos
