# This file is part of Sympathy for Data.
# Copyright (c) 2013 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import (
    print_function, division, unicode_literals, absolute_import)
import os
import shutil
import six
import PySide.QtCore as QtCore

from . import settings


class FilenameException(BaseException):
    pass


class FilenameManager(QtCore.QObject):
    def __init__(self, parent=None):
        super(FilenameManager, self).__init__(parent)
        self._allocated_filenames = {}
        self._unique_numbers = []
        self._config_filename = None
        self._prefix = ''

    def allocate_filename(self, full_uuid, port_index, suffix):
        fq_filename = self._generate_unique_filename(suffix)
        port_id = '{}{}'.format(full_uuid, port_index)
        self._allocated_filenames[port_id] = fq_filename
        return fq_filename

    def full_config_filename(self):
        return self._config_filename

    def allocate_config_filename(self, basename):
        if self._config_filename is None:
            self._config_filename = os.path.join(
                settings.instance()['session_folder'], basename)
        else:
            raise FilenameException('Config filename already defined.')
        return self._config_filename

    def deallocate_all_filenames(self):
        for fq_filename in self._allocated_filenames.itervalues():
            self._remove_filename(fq_filename)

    def deallocate_session_folder(self):
        shutil.rmtree(settings.instance()['session_folder'])

    def _remove_filename(self, fq_filename):
        try:
            os.remove(fq_filename)
        except OSError:
            pass

    def _generate_unique_filename(self, suffix):
        if self._unique_numbers:
            unique_number = next(reversed(self._unique_numbers)) + 1
        else:
            unique_number = 0

        self._unique_numbers.append(unique_number)
        filename = '{}.{}'.format(six.text_type(unique_number), suffix)
        session_folder = settings.instance()['session_folder']
        fq_filename = os.path.join(session_folder, '{}_{}'.format(
            self._prefix, filename))
        if os.path.isfile(fq_filename):
            raise IOError('File exists. Unique filename generation FAIL.')
        return fq_filename

    def set_prefix(self, prefix):
        self._prefix = prefix


filename_manager_instance = FilenameManager()


def instance():
    return filename_manager_instance
