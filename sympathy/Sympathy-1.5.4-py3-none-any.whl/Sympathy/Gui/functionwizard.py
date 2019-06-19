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
import io
import six
import PySide.QtGui as QtGui
import PySide.QtCore as QtCore
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from . wizard_helper_functions import (ValidatingLineEdit,
                                       function_name_validator,
                                       SuperWizard, RED_STYLE, GRAY_STYLE)
from . import settings

DATATYPES = {
    0: ('table', 'Table'),
    1: ('adaf', 'ADAF'),
    2: ('datasource', 'Datasource'),
    3: ('text', 'Text'),
    4: ('figure', 'Figure'),
    5: ('<a>', 'Generic'),
    6: ('[table]', 'List of Tables'),
    7: ('[adaf]', 'List of ADAFs'),
    8: ('[datasource]', 'List of Datasources'),
    9: ('[text]', 'List of Texts'),
    10: ('[figure]', 'List of Figures'),
    11: ('[<a>]', 'List of Generics'),
    12: ('(table, table)', '2-tuple example'),
    13: ('(table, adaf, datasource)', '3-tuple example'),
    14: ('(<a>, <a>)', 'Generic 2-tuple'),
    15: ('[(<a>, <a>)]', 'List of generic 2-tuple'),
    16: ('', 'Undecided')}


class CodePreview(QtGui.QTextEdit):
    """
    Specialized TextEdit which shows a placeholder text similar to that of
    QLineEdit.
    """

    def __init__(self, parent=None):
        super(CodePreview, self).__init__(parent)
        self.setLineWrapMode(QtGui.QTextEdit.NoWrap)

    def paintEvent(self, event):
        if self.hasFocus() or self.toPlainText():
            super(CodePreview, self).paintEvent(event)
        else:
            painter = QtGui.QPainter(self.viewport())
            painter.drawText(self.viewport().geometry(),
                             QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter,
                             "Code preview")

    def set_code(self, code):
        self.setHtml(
            highlight(code, PythonLexer(), HtmlFormatter(
                style='colorful', full=True)))


class FunctionWizardPage(QtGui.QWizardPage):
    _RED = 'red'
    _GRAY = '#e6e6e6'

    def __init__(self, title, model, parent=None):
        super(FunctionWizardPage, self).__init__(parent)
        self._model = model

        # Path
        self._new_file = QtGui.QRadioButton('Create new file')
        self._new_file.setChecked(True)
        self._new_file.setFocusPolicy(QtCore.Qt.NoFocus)
        self._new_path = QtGui.QLineEdit()
        self._new_path.setReadOnly(True)
        self._new_path.setFocusPolicy(QtCore.Qt.NoFocus)
        self._new_button = QtGui.QPushButton('...')
        self._new_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self._existing_file = QtGui.QRadioButton('Add to existing file')
        self._existing_file.setFocusPolicy(QtCore.Qt.NoFocus)
        self._existing_path = QtGui.QLineEdit()
        self._existing_path.setReadOnly(True)
        self._existing_path.setFocusPolicy(QtCore.Qt.NoFocus)
        self._existing_button = QtGui.QPushButton('...')
        self._existing_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self._file_group = QtGui.QButtonGroup()
        self._file_group.addButton(self._new_file)
        self._file_group.addButton(self._existing_file)
        self._type = QtGui.QLineEdit()

        size = self._new_path.sizePolicy()
        size.setHorizontalStretch(1)
        self._new_path.setSizePolicy(size)
        size = self._existing_path.sizePolicy()
        size.setHorizontalStretch(1)
        self._existing_path.setSizePolicy(size)

        # Function name
        self._name = ValidatingLineEdit(function_name_validator)

        # Type
        self._type_dropdown = QtGui.QComboBox()
        for key in DATATYPES:
            self._type_dropdown.addItem(DATATYPES[key][1])
        self._type_dropdown.setMinimumWidth(145)
        self._type_dropdown.setMaximumWidth(145)

        # Preview
        self._preview = CodePreview()
        self._preview.setReadOnly(True)

        # Layout
        layout = QtGui.QGridLayout()
        layout.addWidget(self._new_file, 0, 0, 1, 1)
        layout.addWidget(self._new_path, 0, 1, 1, 2)
        layout.addWidget(self._new_button, 0, 3, 1, 1)
        layout.addWidget(self._existing_file, 1, 0, 1, 1)
        layout.addWidget(self._existing_path, 1, 1, 1, 2)
        layout.addWidget(self._existing_button, 1, 3, 1, 1)
        layout.addWidget(QtGui.QLabel('Function name'), 2, 0, 1, 1)
        layout.addWidget(self._name, 2, 1, 1, 3)
        layout.addWidget(QtGui.QLabel('Input type'), 3, 0, 1, 1)
        layout.addWidget(self._type_dropdown, 3, 1, 1, 1)
        layout.addWidget(QtGui.QLabel('Custom type'), 4, 0, 1, 1)
        layout.addWidget(self._type, 4, 1, 1, 1)
        layout.addWidget(self._preview, 5, 0, 1, 4)
        self.setLayout(layout)

        # Connections
        self._name.validated.connect(self._set_function_name)
        self._file_group.buttonClicked.connect(self._set_file_or_folder)
        self._new_button.clicked.connect(self._get_folder_path)
        self._existing_button.clicked.connect(self._get_file_path)
        self._type.textChanged.connect(self._set_type_lineedit)
        self._type_dropdown.currentIndexChanged.connect(
            self._set_type_dropdown)

        # Final setup
        self._set_disabled()
        self._set_type_dropdown()
        self.setTitle(title)
        self.setFinalPage(True)
        self._update()

    def isComplete(self):
        return (
            len(self._model.get_path()) and
            len(self._model.get_function_name()))

    def _set_file_or_folder(self):
        self._model.clear()
        self._set_type_lineedit()
        self._set_function_name()
        self._set_disabled()

    def _set_function_name(self):
        self._model.set_function_name(self._name.text())
        self._model.set_function()
        self._update()

    def _set_type_dropdown(self):
        index = self._type_dropdown.currentIndex()
        self._type.setText(DATATYPES[index][0])
        self._set_type_lineedit()

    def _set_type_lineedit(self):
        self._model.set_type(self._type.text())
        self._model.set_function()
        self._update()

    def _get_file_path(self):
        # Find a good directory to present in the file dialog.
        old_path = self._model.get_path()
        if old_path:
            directory = old_path
        else:
            directory = settings.instance()['default_folder']

        path = QtGui.QFileDialog.getOpenFileName(
            self, "Select File", directory, filter="Python files (*.py)")
        if len(path[0]):
            self._existing_path.setText(path[0])
            self._model.set_path(path[0])
            self._get_file()
            self._update()

    def _get_folder_path(self):
        # Find a good directory to present in the file dialog.
        old_path = self._model.get_path()
        if old_path:
            default_path = old_path
        else:
            default_path = settings.instance()['default_folder']

        path = QtGui.QFileDialog.getSaveFileName(
            self, "Save File", default_path, filter="Python files (*.py)")
        if len(path[0]):
            self._new_path.setText(path[0])
            self._model.set_path(path[0])
            self._update()

    def _get_file(self):
        path = self._model.get_path()
        if path.endswith('.py'):
            try:
                with io.open(path, 'r', encoding='utf8') as f:
                    self._model.set_code(f.read())
                return
            except (IOError, OSError):
                QtGui.QMessageBox.warning(
                    self, 'File error',
                    "The file cannot be read, "
                    "possibly because of a permission error.")
            except:
                QtGui.QMessageBox.warning(
                    self, 'Unknown file error',
                    "The file cannot be read for an unknown reason.")
        elif len(path):
            QtGui.QMessageBox.warning(
                self, 'File error', 'The file is not a Python file.')
        self._model.set_code('')

    def _set_disabled(self):
        new = self._new_file.isChecked()
        self._existing_path.setDisabled(new)
        self._existing_button.setDisabled(new)
        self._new_path.setEnabled(new)
        self._new_button.setEnabled(new)
        self._new_path.clear()
        self._existing_path.clear()

    def _update(self):
        new = self._new_file.isChecked()
        if new:
            self._existing_path.setStyleSheet(GRAY_STYLE)
            if not len(self._new_path.text()):
                self._new_path.setStyleSheet(RED_STYLE)
            else:
                self._new_path.setStyleSheet(GRAY_STYLE)
        else:
            self._new_path.setStyleSheet(GRAY_STYLE)
            if not len(self._existing_path.text()):
                self._existing_path.setStyleSheet(RED_STYLE)
            else:
                self._existing_path.setStyleSheet(GRAY_STYLE)

        code = self._model.get_code()
        if len(code):
            self._preview.set_code(code)
        else:
            self._preview.set_code('')
        self._preview.verticalScrollBar().setValue(
            self._preview.verticalScrollBar().maximum())
        self.completeChanged.emit()


class FunctionWizard(SuperWizard):
    def __init__(self, parent=None):
        super(FunctionWizard, self).__init__('Function wizard', parent)
        self._model = FunctionWizardModel()

        self._wizard_page = FunctionWizardPage(
            'Function Creator', self._model, self)
        self.addPage(self._wizard_page)

    def done(self, result):
        if result == QtGui.QDialog.Accepted:
            try:
                with io.open(
                        self._model.get_path(), 'w', encoding='utf8') as f:
                            f.write(self._model.get_code())
                super(FunctionWizard, self).done(result)
            except (IOError, OSError):
                QtGui.QMessageBox.warning(
                    self, 'File error',
                    'The file cannot be written, ' +
                    'possibly because of a permission error.')
            except:
                QtGui.QMessageBox.warning(
                    self, 'Unknown file error',
                    "The file cannot be written for an unknown reason.")
                super(FunctionWizard, self).reject()
        else:
            super(FunctionWizard, self).done(result)


class FunctionWizardModel(QtCore.QObject):
    @staticmethod
    def _error_text(tabs):
        msg = '\n'
        for i in range(tabs):
            msg += '    '
        msg += (
            "raise NotImplementedError(" +
            "'Replace the example with your code.')\n\n")
        return six.text_type(msg)

    _IMPORTS = {
        'future': ('from __future__ import ('
                   'print_function, division, unicode_literals,\n'
                   '                        absolute_import)'),
        'any': 'from sympathy.api import fx_wrapper',
        'table': 'from sympathy.api import table',
        'adaf': 'from sympathy.api import adaf'}

    _HELP = (
        "        # See the{}API description in the Help (under Data type\n"
        "        # APIs) for more information on how to write functions.\n")

    _TABLE_EXAMPLE = (
        "        in_table = self.arg\n" +
        "        out_table = self.res\n" +
        _error_text.__func__(2) +
        "        out_table.source(in_table)\n")

    _TABLES_EXAMPLE = (
        "        for in_table in self.arg:\n" +
        "            out_table = table.File()\n" +
        _error_text.__func__(3) +
        "            self.res.append(out_table)\n")

    _ADAF_EXAMPLE = (
        "        in_adaf = self.arg\n" +
        "        out_adaf = self.res\n" +
        _error_text.__func__(2) +
        "        out_adaf.source(in_adaf)\n")

    _ADAFS_EXAMPLE = (
        "        for in_adaf in self.arg:\n" +
        "            out_adaf = adaf.File()\n" +
        _error_text.__func__(3) +
        "            self.res.append(out_adaf)\n")

    _OTHER_EXAMPLE = _error_text.__func__(2)[0:-1]

    _EXAMPLES = {
        'table': _HELP.format(' Table ') + _TABLE_EXAMPLE,
        '[table]': _HELP.format(' Table ') + _TABLES_EXAMPLE,
        'adaf': _HELP.format(' ADAF ') + _ADAF_EXAMPLE,
        '[adaf]': _HELP.format(' ADAF ') + _ADAFS_EXAMPLE,
        'other': _HELP.format(' ') + _OTHER_EXAMPLE}

    def __init__(self):
        self.clear()

    def clear(self):
        self._file_path = ''
        self._function_name = ''
        self._function = ''
        self._type = ''
        self._code = ''
        self._header = ''

    def set_path(self, path):
        self._file_path = path

    def set_function_name(self, name):
        self._function_name = name
        self._camel_case()

    def set_type(self, type_):
        self._type = type_

    def set_code(self, code):
        self._code = code

    def set_function(self):
        self._function = '\n\n' + (
            'class {}(fx_wrapper.FxWrapper):\n'
            '    """Add function documentation here"""\n\n'
            '    arg_types = [{}]\n\n'
            '    def execute(self):\n').format(
            self._function_name, "'" + self._type + "'")

        try:
            self._function += self._EXAMPLES[DATATYPES[self._type][0]]
        except KeyError:
            self._function += self._EXAMPLES['other']
        self._set_header()

        try:
            str(self._function)
        except UnicodeEncodeError:
            self._code = '# -*- coding: utf-8 -*-\n' + self._code

    def get_path(self):
        return self._file_path

    def get_function_name(self):
        return self._function_name

    def get_code(self):
        if (self._code.find('class ' + self._function_name + '(') == -1 and
                len(self._function_name)):
            return self._header + self._code + self._function
        return ''

    def _set_header(self):
        self._header = ''
        if self._type not in ['table', '[table]', 'adaf', '[adaf]']:
            key = 'any'
        else:
            key = self._type
        key = key.replace('[', '')
        key = key.replace(']', '')
        if self._code.find(self._IMPORTS['future']) == -1:
            self._header += self._IMPORTS['future'] + '\n'
        if self._code.find(self._IMPORTS['any']) == -1:
            self._header += self._IMPORTS['any'] + '\n'
        if (self._code.find(self._IMPORTS[key]) == -1 and
                self._header.find(self._IMPORTS[key]) == -1):
            self._header += self._IMPORTS[key] + '\n'

    def _camel_case(self):
        self._function_name = ''.join(
            [word[0].upper() + word[1:].lower()
                for word in self._function_name.split()])
