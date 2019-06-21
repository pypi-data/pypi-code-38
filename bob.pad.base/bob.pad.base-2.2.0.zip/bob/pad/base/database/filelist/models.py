#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Pavel Korshunov <pavel.korshunov@idiap.ch>
# @date:   Thu Nov 17 16:09:22 CET 2016
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
This file defines simple Client and File interfaces that are comparable with other bob.db databases.
"""

import os
import fileinput
import re
from bob.pad.base.database import PadFile


class Client(object):
    """
    The clients of this database contain ONLY client ids. Nothing special.
    """

    def __init__(self, client_id):
        self.id = client_id
        """The ID of the client, which is stored as a :py:class:`str` object."""


class FileListFile(PadFile):
    """
     Initialize the File object with the minimum required data.

     **Parameters**

     path : str
       The path of this file, relative to the basic directory.
       Please do not specify any file extensions.
       This path will be used as an underlying file_id, as it is assumed to be unique

     client_id : various type
       The id of the client, this file belongs to.
       The type of it is dependent on your implementation.
       If you use an SQL database, this should be an SQL type like Integer or String.
    """

    def __init__(self, file_name, client_id, attack_type=None):
        super(FileListFile, self).__init__(client_id=client_id, path=file_name, attack_type=attack_type, file_id=file_name)


#############################################################################
### internal access functions for the file lists; do not export!
#############################################################################

class ListReader(object):
    def __init__(self, store_lists):
        self.m_read_lists = {}
        self.m_store_lists = store_lists

    def _read_multi_column_list(self, list_file):
        rows = []
        if not os.path.isfile(list_file):
            raise RuntimeError('File %s does not exist.' % (list_file,))
        try:
            for line in fileinput.input(list_file):
                parsed_line = re.findall('[\w/(-.)]+', line)
                if len(parsed_line):
                    # perform some sanity checks
                    if len(parsed_line) not in (2, 3):
                        raise IOError("The read line '%s' from file '%s' could not be parsed successfully!" %
                                      (line.rstrip(), list_file))
                    if len(rows) and len(rows[0]) != len(parsed_line):
                        raise IOError("The parsed line '%s' from file '%s' has a different number of elements "
                                      "than the first parsed line '%s'!" % (parsed_line, list_file, rows[0]))
                    # append the read line
                    rows.append(parsed_line)
            fileinput.close()
        except IOError as e:
            raise RuntimeError("Error reading the file '%s' : '%s'." % (list_file, e))

        # return the read list as a vector of columns
        return rows

    def _read_column_list(self, list_file, column_count):
        # read the list
        rows = self._read_multi_column_list(list_file)
        # extract the file from the first two columns
        file_list = []
        for row in rows:
            if column_count == 2:
                assert len(row) == 2
                # we expect: filename client_id
                file_list.append(FileListFile(file_name=row[0], client_id=row[1]))
            elif column_count == 3:
                assert len(row) == 3
                # we expect: filename, model_id, client_id
                file_list.append(FileListFile(file_name=row[0], client_id=row[1], attack_type=row[2]))
            else:
                raise ValueError("The given column count %d cannot be interpreted. This is a BUG, please "
                                 "report to the author." % column_count)

        return file_list

    def read_list(self, list_file, group, type=None):
        """Reads the list of Files from the given list file (if not done yet) and returns it."""
        if group not in self.m_read_lists:
            self.m_read_lists[group] = {}
        if type not in self.m_read_lists[group]:
            if type == 'for_real':
                files_list = self._read_column_list(list_file, 2)
            elif type == 'for_attack':
                files_list = self._read_column_list(list_file, 3)
            else:
                raise ValueError("The given type must be one of %s, but not '%s'" % (('for_real', 'for_attack'), type))
            if self.m_store_lists:
                self.m_read_lists[group][type] = files_list
            return files_list
        return self.m_read_lists[group][type]
