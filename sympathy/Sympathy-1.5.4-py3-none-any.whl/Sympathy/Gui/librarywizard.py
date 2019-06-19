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
import os
import shutil
import codecs
import re
import PySide.QtGui as QtGui
import PySide.QtCore as QtCore
from Gui import settings
from . wizard_helper_functions import (ValidatingLineEdit,
                                       python_identifier_validator,
                                       name_validator,
                                       identifier_validator,
                                       string_to_identifier,
                                       format_python_string,
                                       RED_STYLE, GRAY_STYLE,
                                       SuperWizard, LIBRARY_INI, create_ini)


NODE_NAMES = [
    'Hello world example',
    'Hello world customizable example',
    'Output example',
    'Error example',
    'All parameters example',
    'Progress example',
    'Controller example',
    'Read/write example'
]

PLUGIN = 'plugin_calculator.py'


class LibraryWizardDirectoryPage(QtGui.QWizardPage):
    def __init__(self, title, model, parent=None):

        super(LibraryWizardDirectoryPage, self).__init__(parent)
        self._model = model

        self._lib_path = QtGui.QLineEdit()
        self._lib_path.setFocusPolicy(QtCore.Qt.NoFocus)
        self._lib_path.setReadOnly(True)
        self._lib_path.setStyleSheet(RED_STYLE)
        self._path_btn = QtGui.QPushButton('...')
        self._com_pkg_name = ValidatingLineEdit(python_identifier_validator)
        self._com_pkg_name.setStyleSheet(GRAY_STYLE)

        self._com_pkg_name.setMaxLength(40)
        self._com_pkg_name.setToolTip(
            'Set the name of the Common package, where code shared between '
            'nodes may be placed. Default name is the same as the library '
            'name sans whitespace.')

        self._lib_preview = QtGui.QTreeWidget()
        self._lib_preview.header().close()
        self._create_base_tree()
        self._lib_preview.insertTopLevelItem(0, self._top_level_item)
        self._top_level_item.setHidden(True)

        layout = QtGui.QGridLayout()
        layout.addWidget(QtGui.QLabel('Library path'), 0, 0, 1, 1)
        layout.addWidget(self._lib_path, 0, 1, 1, 1)
        layout.addWidget(self._path_btn, 0, 2, 1, 1)
        layout.addWidget(QtGui.QLabel('Common package name'), 1, 0, 1, 1)
        layout.addWidget(self._com_pkg_name, 1, 1, 1, 2)
        layout.addWidget(QtGui.QLabel(
            'Library file structure preview'), 2, 0, 1, 1)
        layout.addWidget(self._lib_preview, 3, 0, 1, 3)
        self.setLayout(layout)

        self._path_btn.clicked.connect(self._get_directory_path)
        self._com_pkg_name.validated.connect(self._set_com_pkg_name)

        self.setFinalPage(True)
        self.setTitle(title)
        self._update()

    def isComplete(self):
        return (
            self._com_pkg_name.isValid() and
            len(self._model.library_path))

    def initializePage(self):
        self._model.validate()
        self._com_pkg_name.setText(self._model.library_package_name)

    def _create_base_tree(self):
        icon_provider = QtGui.QFileIconProvider()
        folder_icon = icon_provider.icon(QtGui.QFileIconProvider.Folder)
        file_icon = icon_provider.icon(QtGui.QFileIconProvider.File)

        self._top_level_item = QtGui.QTreeWidgetItem()
        self._top_level_item.setIcon(0, folder_icon)

        common = self._add_item_to_tree(
            self._top_level_item, folder_icon, 'Common')
        library = self._add_item_to_tree(
            self._top_level_item, folder_icon, 'Library')
        self._add_item_to_tree(
            self._top_level_item, folder_icon, 'Test')
        self._info = self._add_item_to_tree(
            self._top_level_item, file_icon, LIBRARY_INI)

        self._com_libname = self._add_item_to_tree(common, folder_icon)
        self._lib_libname = self._add_item_to_tree(library, folder_icon)

        self._add_item_to_tree(
            self._com_libname, file_icon, '__init__.py')
        self._add_item_to_tree(
            self._com_libname, file_icon, PLUGIN)

        self._add_item_to_tree(
            self._lib_libname, file_icon, 'node_examples.py')
        self._add_item_to_tree(
            self._lib_libname, file_icon, 'example.svg')
        self._add_item_to_tree(
            self._lib_libname, file_icon, 'example_error.svg')

    def _add_item_to_tree(self, parent, icon, name=''):
        item = QtGui.QTreeWidgetItem()
        item.setIcon(0, icon)
        item.setText(0, name)
        parent.addChild(item)
        return item

    def _get_directory_path(self):
        old = self._model.library_path
        default_path = ('../' + old if len(old) else
                        settings.instance()['default_folder'])
        path = QtGui.QFileDialog.getExistingDirectory(
            self, "Create Library", default_path)
        self._model.library_path = path if len(path) else old
        self._update()

    def _set_com_pkg_name(self):
        self._model.common_package_name = self._com_pkg_name.text()
        self._update()

    def _update_preview(self):
        if self.isComplete():
            self._top_level_item.setText(0, self._model.library_path)
            self._com_libname.setText(0, self._model.common_package_name)
            self._lib_libname.setText(0, self._model.library_package_name)
            self._top_level_item.setHidden(False)
            self._lib_preview.expandAll()
        else:
            self._top_level_item.setHidden(True)
        self._model.structure = QtGui.QTreeWidgetItemIterator(
            self._lib_preview, QtGui.QTreeWidgetItemIterator.NoChildren)

    def _update(self):
        self._lib_path.setText(self._model.library_path)
        if not self._lib_path.text():
            self._lib_path.setStyleSheet(RED_STYLE)
        else:
            self._lib_path.setStyleSheet(GRAY_STYLE)
        self._update_preview()
        self.completeChanged.emit()


class LibraryWizardMetaPage(QtGui.QWizardPage):
    def __init__(self, title, model, parent=None):
        super(LibraryWizardMetaPage, self).__init__(parent)
        self._model = model
        self._id_changed = False

        self._name = ValidatingLineEdit(name_validator)
        self._description = QtGui.QLineEdit()
        self._identifier = ValidatingLineEdit(identifier_validator)
        self._copyright = QtGui.QLineEdit()
        self._repo_path = QtGui.QLineEdit()

        self._name.setMaxLength(40)
        self._description.setMaxLength(256)
        self._identifier.setMaxLength(40)
        self._copyright.setMaxLength(256)
        self._repo_path.setMaxLength(256)

        self._description.setStyleSheet(GRAY_STYLE)
        self._copyright.setStyleSheet(GRAY_STYLE)
        self._repo_path.setStyleSheet(GRAY_STYLE)

        self._name.setToolTip(
            "The name of the library which will be displayed in Sympathy's "
            "library view. Mandatory.")
        self._description.setToolTip(
            'A small description of the library. Optional.')
        self._identifier.setToolTip(
            'A string that will be used in the nodes to give them a unique id.'
            'For example, the identifier "test" will result in nodes with an '
            'id on the form "test.examplenode". Mandatory.')
        self._copyright.setToolTip(
            'A copyright message. Optional.')
        self._repo_path.setToolTip(
            'A repository path to the library. Optional.')

        layout = QtGui.QFormLayout()
        layout.addRow('Library name', self._name)
        layout.addRow('Description', self._description)
        layout.addRow('Identifier', self._identifier)
        layout.addRow('Copyright', self._copyright)
        layout.addRow('Repository URL', self._repo_path)
        layout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.setLayout(layout)

        self._name.validated.connect(self._meta_changed)
        self._description.textChanged.connect(self._meta_changed)
        self._identifier.validated.connect(self._identifier_changed)
        self._copyright.textChanged.connect(self._meta_changed)
        self._repo_path.textChanged.connect(self._meta_changed)

        self.setTitle(title)

    def isComplete(self):
        return (
            len(self._model.identifier) and
            len(self._model.library_name) and
            self._name.isValid() and
            self._identifier.isValid())

    def _meta_changed(self):
        if self._name.isValid() or not len(self._name.text()):
            self._model.library_name = self._name.text()
        self._model.description = self._description.text()
        self._model.copyright = self._copyright.text()
        self._model.repo = self._repo_path.text()
        self._update()

    def _identifier_changed(self):
        if self.focusWidget() == self._identifier:
            self._id_changed = True
        if self._identifier.isValid() or not len(self._identifier.text()):
            self._model.identifier = self._identifier.text()
        self._update()

    def _update(self):
        if not self._id_changed:
            identifier = string_to_identifier(self._model.library_name)
            self._identifier.setText(identifier)
            self._model.identifier = identifier
        self.completeChanged.emit()


class LibraryWizard(SuperWizard):
    def __init__(self, parent=None):
        super(LibraryWizard, self).__init__('Library wizard', parent)
        self._model = LibraryWizardModel()

        meta_page = LibraryWizardMetaPage(
            'Library information', self._model, self)
        directory_page = LibraryWizardDirectoryPage(
            'Library location', self._model, self)
        self.addPage(meta_page)
        self.addPage(directory_page)

    def done(self, result):
        if result == QtGui.QDialog.Accepted:
            success = self._create_file_structure()
            if success:
                self._add_library_to_settings()
                super(LibraryWizard, self).done(result)
        if result == QtGui.QDialog.Rejected:
            super(LibraryWizard, self).done(result)

    def _create_file_structure(self):
        path = self._model.library_path
        if os.path.isdir(path):
            QtGui.QMessageBox.warning(
                self, 'Creation error',
                'The folder already exists, choose another location.')
            return False
        for path in self._model.structure:
            _, ext = os.path.splitext(path)
            folder = os.path.dirname(path)
            try:
                if len(ext):
                    if not os.path.isdir(folder):
                        os.makedirs(folder)
                    self._create_example_file(path)
                elif not os.path.isdir(path):
                    os.makedirs(path)
            except (OSError, IOError):
                QtGui.QMessageBox.warning(
                    self, 'Creation error',
                    'The Library cannot be created, ' +
                    'possibly because of a permission error.')
                self._cleanup()
                return False
            except:
                QtGui.QMessageBox.warning(
                    self, 'Creation error',
                    'The Library cannot be created. Reason unknown.')
                self._cleanup()
                return False
        return True

    def _add_library_to_settings(self):
        setting = settings.instance()
        libraries = setting['Python/library_path']
        libraries.append(self._model.library_path)
        setting['Python/library_path'] = libraries

    def _create_example_file(self, path):
        setting = settings.instance()
        EXAMPLE_FOLDER = (  # noqa
            setting['install_folder'] +
            '/../Library/Library/sympathy/examples/')
        if path.endswith('node_examples.py'):
            with codecs.open(
                    self._prepare_path(EXAMPLE_FOLDER + 'node_examples.py'),
                    encoding='utf-8') as file:
                example = ''
                for line in file:
                    example += line
                file.close()
                name, ext = os.path.splitext(path)
                new_path = '{}_{}{}'.format(
                    name, self._model.library_name, ext)
                file = codecs.open(new_path, 'w', encoding='utf-8')
                example = example.replace(
                    'org.sysess.sympathy', self._model.identifier)
                for name in NODE_NAMES:
                    example = example.replace(
                        name, '{} ({})'.format(name, self._model.library_name))
                file.write(example)
        elif path.endswith('example.svg'):
            shutil.copyfile(
                self._prepare_path(EXAMPLE_FOLDER + 'example.svg'), path)
        elif path.endswith('example_error.svg'):
            shutil.copyfile(
                self._prepare_path(EXAMPLE_FOLDER + 'example_error.svg'), path)
        elif path.endswith('__init__.py'):
            open(path, 'a').close()
        elif path.endswith(LIBRARY_INI):
            create_ini(
                path, self._model.library_name, self._model.description,
                self._model.identifier, self._model.library_package_name,
                self._model.common_package_name, self._model.copyright,
                self._model.repo)
        elif path.endswith(PLUGIN):
            self._create_example_plugin()

    def _create_example_plugin(self):
        plugin_path = os.path.join(
            settings.instance()['install_folder'],
            'Examples/CalculatorPlugin/plugin_example.py')
        plugin_path = self._prepare_path(plugin_path)
        with codecs.open(plugin_path, encoding='utf-8') as file:
            plugin = file.read()

        copyright = 'POSSIBILITY OF SUCH DAMAGE.'
        copyright_end_index = (
            plugin.find(copyright) + len(copyright) + len('\n'))
        plugin = plugin[copyright_end_index:]
        plugin = plugin.replace(
            'custom_plugin', self._model.library_name.lower(), 1)
        plugin = plugin.replace('CustomPlugin', self._model.library_name, 1)

        new_path = os.path.join(
            self._model.library_path, 'Common',
            self._model.library_package_name, PLUGIN)
        with codecs.open(self._prepare_path(new_path), 'w') as file:
            file.write(plugin)

    def _prepare_path(self, path):
        return os.path.normpath(os.path.realpath(path))

    def _cleanup(self):
        """If something was created but then failed, remove everything."""
        try:
            if os.path.isdir(self._model.library_path):
                shutil.rmtree(self._model.library_path)
        except:
            pass


class LibraryWizardModel(QtCore.QObject):

    def __init__(self):
        self._lib_name = ''
        self._lib_path = ''
        self._com_pkg_name = ''
        self._paths = []
        self._description = ''
        self._identifier = ''
        self._copyright = ''
        self._repo = ''

    def validate(self):
        self._lib_name = self._lib_name.strip()
        if self.identifier[-1] == '.':
            self._identifier = self.identifier[:-1]

    @property
    def library_name(self):
        return self._lib_name

    @library_name.setter
    def library_name(self, value):
        value = value.strip()
        self._lib_name = value
        pkg_name = format_python_string(value).lower()
        self._com_pkg_name = pkg_name

    @property
    def library_package_name(self):
        return self._com_pkg_name

    @property
    def common_package_name(self):
        return self._com_pkg_name

    @common_package_name.setter
    def common_package_name(self, value):
        self._com_pkg_name = value

    @property
    def library_path(self):
        return self._lib_path

    @library_path.setter
    def library_path(self, value):
        self._lib_path = os.path.normpath(value + '/' + self._lib_name)

    @property
    def structure(self):
        return self._paths

    @structure.setter
    def structure(self, value):
        self._paths = []
        while value.value():
            child = value.value()
            parent = child.parent()
            path = child.text(0)
            while parent:
                path = parent.text(0) + '/' + path
                parent = parent.parent()
            self._paths.append(os.path.normpath(path))
            next(value)

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def identifier(self):
        return self._identifier

    @identifier.setter
    def identifier(self, value):
        value = re.sub('[^a-z0-9\\.]', '', value.lower())
        self._identifier = value

    @property
    def copyright(self):
        return self._copyright

    @copyright.setter
    def copyright(self, value):
        self._copyright = value

    @property
    def repo(self):
        return self._repo

    @repo.setter
    def repo(self, value):
        self._repo = value
