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
import PySide.QtCore as QtCore
import PySide.QtGui as QtGui

import os
import copy


SETTINGS_MAJOR_VERSION = 2
SETTINGS_MINOR_VERSION = 0
SETTINGS_MAINTENANCE_VERSION = 0

settings_instance = None

# Default values for settings that will be written to the preferences file.
permanent_defaults = {
    'Debug/graphviz_path': '',
    'Debug/profile_path_type': 'Session folder',
    'Gui/grid_spacing': 25,
    'Gui/library_type': 'Tag layout',
    'Gui/library_hide': False,
    'Gui/library_matcher_type': 'character',
    'Gui/library_highlighter_type': 'background-color',
    'Gui/library_highlighter_color': '#EECC22',
    'Gui/quickview_popup_position': 'center',
    'Gui/recent_flows': [],
    'Gui/snap_type': 'Grid',
    'Gui/system_editor': False,
    'Gui/nodeconfig_confirm_cancel': True,
    'Gui/code_editor_theme': "colorful",
    'Gui/docking_enabled': 'Detachable',
    'Gui/flow_connection_shape': 'Spline',
    'Gui/experimental': False,
    'Python/library_path': ['../Library'],
    'Python/recent_library_path': [],
    'Python/python_path': [],
    'MATLAB/matlab_path': '',
    'MATLAB/matlab_jvm': True,
    'ask_for_save': True,
    'new_flow_on_start': True,
    'environment': [],
    'max_task_chars': 32000,
    'max_temp_folder_age': 3,
    'max_temp_folder_number': 100,
    'max_temp_folder_size': '1 G',
    'remove_temp_files': True,
    'save_session': False,
    'session_files': [],
    'temp_folder': os.path.join(os.path.normpath(
        QtGui.QDesktopServices.storageLocation(
            QtGui.QDesktopServices.StandardLocation.CacheLocation)),
        'Sympathy for Data'),
    'default_folder': os.path.join(os.path.normpath(
        QtGui.QDesktopServices.storageLocation(
            QtGui.QDesktopServices.StandardLocation.DocumentsLocation)),
        'Sympathy for Data'),
    'max_nbr_of_threads': 0,
    'deprecated_warning': False,
}


def to_list(value):

    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def to_bool(value):

    if value == 'true':
        return True
    else:
        return False


# Types for settings that will be written to the preferences file.
# None means, value returned as is.
permanent_types = {
    'Debug/graphviz_path': None,
    'Debug/profile_path_type': None,
    'Gui/geometry': None,
    'Gui/grid_spacing': int,
    'Gui/library_type': None,
    'Gui/library_hide': to_bool,
    'Gui/library_matcher_type': None,
    'Gui/library_highlighter_type': None,
    'Gui/library_highlighter_color': None,
    'Gui/quickview_popup_position': None,
    'Gui/recent_flows': to_list,
    'Gui/snap_type': None,
    'Gui/system_editor': to_bool,
    'Gui/code_editor_theme': None,
    'Gui/window_state': None,
    'Gui/nodeconfig_confirm_cancel': to_bool,
    'Gui/docking_enabled': None,
    'Gui/flow_connection_shape': None,
    'Gui/experimental': to_bool,
    'Python/library_path': to_list,
    'Python/recent_library_path': to_list,
    'Python/python_path': to_list,
    'MATLAB/matlab_path': None,
    'MATLAB/matlab_jvm': to_bool,
    'ask_for_save': to_bool,
    'new_flow_on_start': to_bool,
    'environment': to_list,
    'grid_spacing': float,
    'max_task_chars': int,
    'max_temp_folder_age': int,
    'max_temp_folder_number': int,
    'max_temp_folder_size': None,
    'remove_temp_files': to_bool,
    'save_session': to_bool,
    'session_files': to_list,
    'temp_folder': None,
    'default_folder': None,
    'max_nbr_of_threads': int,
    'config_file_version': None,
    'deprecated_warning': to_bool,
}


# These settings will be available in worker processes.
worker_settings = [
    'Gui/code_editor_theme',
    'Gui/nodeconfig_confirm_cancel',
    'MATLAB/matlab_path',
    'MATLAB/matlab_jvm',
    'default_folder',
    'session_folder',
    'deprecated_warning',
    'Debug/graphviz_path',
    'max_task_chars',
]


def get_worker_settings():
    """
    Return a dictionary with all the settings that should be exposed to the
    worker.
    """
    return {k: instance()[k] for k in worker_settings}


class Settings(object):

    def __init__(self, ini_file_name=None):
        super(Settings, self).__init__()
        self._file_name = ini_file_name
        self._permanent_storage = None
        self._temporary_storage = {}
        self._error = False
        self._init()

    def _init(self):
        if self._file_name:
            self.set_ini_file(self._file_name)
        else:
            self._permanent_storage = QtCore.QSettings(
                QtCore.QSettings.IniFormat, QtCore.QSettings.UserScope,
                'Sysess', 'Sympathy_1.3')

            if len(self._permanent_storage.allKeys()) == 0:
                self._update_version()

            self._error = not self._check_version()

    def _check_version(self):
        version = self._permanent_storage.value(
            'config_file_version', '0.0.0').split('.')
        major_version = int(version[0])
        minor_version = int(version[1])
        # maintenance_version = int(version[2])
        version_is_supported = ((major_version == SETTINGS_MAJOR_VERSION) and
                                (minor_version <= SETTINGS_MINOR_VERSION))
        if (version_is_supported):
            self._update_version()

        return version_is_supported

    def _update_version(self):
        self['config_file_version'] = '{}.{}.{}'.format(
            SETTINGS_MAJOR_VERSION,
            SETTINGS_MINOR_VERSION,
            SETTINGS_MAINTENANCE_VERSION)

    def set_ini_file(self, file_name):
        self._error = False
        self._file_name = file_name

        new_file = os.path.exists(file_name)

        self._permanent_storage = QtCore.QSettings(
            self._file_name, QtCore.QSettings.IniFormat)
        if new_file:
            self._update_version()
        else:
            self._error = not self._check_version()

    def keys(self):
        return (self._permanent_storage.allKeys() +
                self._temporary_storage.keys())

    def clear(self):
        self._permanent_storage.clear()
        self._temporary_storage.clear()
        self._error = False
        self._update_version()

    def error(self):
        return self._error

    def file_name(self):
        return self._file_name

    def __contains__(self, key):
        if key in permanent_defaults:
            return True
        elif key in permanent_types and self._permanent_storage.contains(key):
            return True
        return key in self._temporary_storage

    def __getitem__(self, key):
        if key in permanent_types:
            if self._permanent_storage.contains(key):

                value = self._permanent_storage.value(key)
                type_ = permanent_types.get(key)
                if type_:
                    return type_(value)
                return value
            elif key in permanent_defaults:
                return copy.copy(permanent_defaults[key])
            raise KeyError('Settings instance does not have key: "{}"'.
                           format(key))
        else:
            try:
                return copy.copy(self._temporary_storage[key])
            except KeyError:
                raise KeyError('Settings instance does not have key: "{}"'.
                               format(key))

    def __setitem__(self, key, value):
        if key in permanent_types:
            current = self.get(key)

            if current is None or current != value:
                self._permanent_storage.setValue(key, value)
                self._permanent_storage.sync()
        else:
            self._temporary_storage[key] = value

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def sync(self):
        self._permanent_storage.sync()


def create_settings(fq_ini_filename=None):
    global settings_instance
    if settings_instance is not None:
        raise RuntimeError('Settings already instatiated.')
    if fq_ini_filename is None:
        settings_instance = Settings()
    else:
        settings_instance = Settings(fq_ini_filename)


def instance():
    if settings_instance is None:
        create_settings()
    return settings_instance
