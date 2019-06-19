# -*- coding: utf-8 -*-
# This file is part of Sympathy for Data.
# Copyright (c) 2017 Combine Control Systems AB
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
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import PySide.QtCore as QtCore
import PySide.QtGui as QtGui
import inspect
import os
import re
import codecs

from Gui import settings
from sympathy.platform.exceptions import sywarn

RED_STYLE = 'QLineEdit{border: 0.5px solid red}'
GRAY_STYLE = 'QLineEdit{border: 0.5px solid #AEAEAE}'
IDENTIFIER_MAX_LENGTH = 40
ASCII_RANGE = 128
LIBRARY_INI = 'library.ini'


def python_identifier_validator(string):
    """Python compliant identifier name. Max 40 characters."""
    try:
        return (
            len(string) and len(string) <= IDENTIFIER_MAX_LENGTH and
            (re.match('^[A-z][0-9A-z]*$', string) is not None))
    except:
        return False


def function_name_validator(string):
    """Set the function name.
    It can not be empty and can only contain alphanumeric characters
    and spaces and be max 40 characters long
    """
    return (
        len(string) and string[0].isalpha() and
        len(string) < IDENTIFIER_MAX_LENGTH and
        all(x.isalnum() or x.isspace() or x == '_'
            for x in string[1:]) and is_ascii(string))


def identifier_validator(string):
    """Lower case letters, ascii, and dots only, for library identifier"""
    if re.search('\\.\\.', string) is not None:
        return False

    return (
        string != '' and string[0].isalpha() and is_ascii(string) and
        len(string) < IDENTIFIER_MAX_LENGTH and string.islower() and
        all(x.isalnum() or x == '.' for x in string[1:]))


def node_name_validator(string):
    """
    String determines the node name and parts of: classname, filename and
    node identifier.

    It should not be empty and must start with a letter, it should
    only contain ASCII characters.
    """
    return string != '' and string[0].isalpha() and is_ascii(string)


def name_validator(string):
    """
    The string may not be empty and must not start or end with empty
    characters, and not contain illegal Windows characters.
    """
    return (
        string and string == string.strip() and
        not set('\/:*?"<>|').intersection(string))


def port_name_validator(string):
    if not len(string):
        return True
    return string[0].isalpha() and is_ascii(string)


def icon_validator(icon):
    """
    Icon determines the relative filename of the .svg icon file.

    It should be a relative path to a .svg file.
    """
    sep = '\\\\' if os.path.sep == '\\' else os.path.sep
    return icon == '' or re.match('^([^{0}]+{0})*[^{0}]+.svg$'.format(
        sep), icon) is not None


def is_ascii(string):
    return all(ord(char) < ASCII_RANGE for char in string)


def string_to_identifier(string):
    return re.sub('[^a-z0-9]', '', string.lower())


def format_python_string(string):
    """Returns a python compliant identifier string"""
    # Find first letter and remove starting digits if any
    letter_matches = re.search('/^[A-z]+$/', string)
    if letter_matches:
        string = string[letter_matches.start():]
    # Remove characters with modifers (é, ü, etc.)
    string = string.lower().translate(dict((ord(c), None) for c in '´`¨^'))
    # Remove all non-ascii and non-alphanumeric characters except spaces
    string = ''.join(
        c for c in string if (c.isalnum() or c == ' ') and is_ascii(c))
    # Capitalize words separated by whitespace
    string = ''.join([word.title() for word in string.split()])
    return string[:IDENTIFIER_MAX_LENGTH]


def create_ini(
        filename, name, description, identifier, library_path,
        common_path, copyright, repository):
    if not len(name) or not len(library_path):
        sywarn(
            'Mandatory parts of library is missing. '
            'Please create a new library using the Library Wizard.')
        return False
    try:
        with codecs.open(filename, 'w', encoding='utf-8') as file:
            file.write('[General]\r\n')
            file.write('name=' + name + '\r\n')
            file.write('description=' + description + '\r\n')
            file.write('identifier=' + identifier + '\r\n')
            file.write('library_path=' + 'Library/' + library_path + '\r\n')
            if len(common_path):
                file.write('common_path=' + 'Common/' + common_path + '\r\n')
            else:
                file.write('common_path=' + '\r\n')
            file.write('copyright=' + copyright + '\r\n')
            file.write('repository=' + repository + '\r\n')
    except (IOError, OSError):
        sywarn('The file cannot be created, perhaps due to permission errors.')
        return False
    return True


def find_library_info(library_root_path):
    info = {
        'name': '',
        'description': '',
        'identifier': 'example',
        'library_path': '',
        'common_path': '',
        'copyright': '',
        'repository': ''
    }
    library_path = os.path.normpath(library_root_path + '/Library')
    common_path = os.path.normpath(library_root_path + '/Common')
    try:
        for item in os.listdir(library_path):
            if os.path.isdir(os.path.normpath(library_path + '/' + item)):
                info['name'] = item
                info['library_path'] = item
                break
    except OSError:
        # Library folder missing, not valid library, return default values.
        return info

    try:
        for item in os.listdir(common_path):
            if os.path.isdir(os.path.normpath(common_path + '/' + item)):
                info['common_path'] = item
                break
    except OSError:
        # Common folder missing, just continue
        pass

    library_files = []
    for root, _, filenames in os.walk(library_path):
        for filename in filenames:
            if filename.endswith('.py'):
                library_files.append(
                    os.path.normpath(root + '/' + filename))

    done = False
    for item in library_files:
        if os.path.basename(item).startswith('node_'):
            with codecs.open(item, encoding='utf8', mode='r') as file:
                class_id = 'class '
                line_id = 'nodeid = '
                class_name = ''
                while not done:
                    line = file.readline()
                    if line == '':
                        done = True
                        break
                    line = line.strip()
                    class_start = line.find(class_id)
                    class_end = line.find('(')
                    if class_start != -1 and class_end != -1:
                        class_name = line[
                            class_start + len(class_id):class_end]
                        continue
                    id_index = line.find(line_id)
                    if id_index != -1:
                        info['identifier'] = line.replace(
                            line_id, '').replace("'", "").replace(
                            '.' + class_name.lower(), '').rstrip('.')
                        done = True
        if done:
            break
    return info


class ValidatingLineEdit(QtGui.QLineEdit):

    validated = QtCore.Signal()

    def __init__(self, validator, parent=None):
        super(ValidatingLineEdit, self).__init__(parent)
        self._validator = validator
        self._valid = False
        self.textChanged.connect(self.validateText)
        self.setToolTip(inspect.getdoc(validator))
        self.validateText('')

    def isValid(self):
        return self._valid

    def validateText(self, text):
        self._valid = self._validator(text)
        if self._valid:
            self.setStyleSheet(GRAY_STYLE)
        else:
            self.setStyleSheet(RED_STYLE)
        self.validated.emit()

    def validate(self):
        self.validateText(self.text())


class SuperWizard(QtGui.QWizard):
    def __init__(self, title, parent=None):
        super(SuperWizard, self).__init__(parent)
        self.setWindowFlags(
            self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.setWindowTitle(title)
        # On Windows the Wizard shows the WindowTitle in the wrong
        # place if we use the native style
        self.setWizardStyle(QtGui.QWizard.ClassicStyle)
        self._confirm_cancel = settings.instance()[
            'Gui/nodeconfig_confirm_cancel']

    def reject(self):
        if self._confirm_reject():
            super(SuperWizard, self).reject()

    def _confirm_reject(self):
        if self._confirm_cancel:
            result = QtGui.QMessageBox.question(
                self, 'Exit?',
                'The wizard is not complete, are you sure you want to exit?',
                QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
            return result == QtGui.QMessageBox.Ok
        return True
