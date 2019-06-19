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
from collections import OrderedDict
import io
import os
import six

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

from sympathy.utils.prim import uri_to_path
from sympathy.platform import version_support as vs
from . import librarywizard
from .wizard_helper_functions import (ValidatingLineEdit, node_name_validator,
                                      icon_validator, port_name_validator,
                                      SuperWizard, LIBRARY_INI, create_ini,
                                      find_library_info, format_python_string)
import PySide.QtCore as QtCore
import PySide.QtGui as QtGui

MIME_TYPE = 'text/plain'


def get_identifier_from_ini(parent, ini_path):
    try:
        with open(ini_path, 'r') as file:
            for line in file:
                if 'identifier' in line:
                    return line.split(
                        '=')[1].replace('\r', '').replace('\n', '')
    except (OSError, IOError):
        QtGui.QMessageBox.warning(
            parent, 'Error',
            ('Library ini file cannot be found or opened.\n'
             'An ID from an existing node will be used, and if none can be '
             'found, a default ID will be set.\n'
             'The ini file will then be added to the library.'))
    return ''


def format_meta_data(string):
    return string.strip().replace(
        '\\', '\\\\').replace("'", "\\'").replace('"', '\\"')


class PortList(QtGui.QListView):
    changed_selection = QtCore.Signal()
    delete_pressed = QtCore.Signal()

    def __init__(self):
        super(PortList, self).__init__()
        self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.setDragEnabled(True)
        self.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        size = self.sizePolicy()
        size.setVerticalStretch(1)
        self.setSizePolicy(size)

    def dragEnterEvent(self, e):
        super(PortList, self).dragEnterEvent(e)

    def dragMoveEvent(self, e):
        super(PortList, self).dragMoveEvent(e)

    def dropEvent(self, e):
        super(PortList, self).dropEvent(e)

    def keyPressEvent(self, e):
        super(PortList, self).keyPressEvent(e)
        if e.key() == QtCore.Qt.Key_Delete:
            self.delete_pressed.emit()

    def selectionChanged(self, selected, deselected):
        super(PortList, self).selectionChanged(selected, deselected)
        self.changed_selection.emit()


class Port(object):
    def __init__(self, name, type, description):
        self._name = name
        self._type = type
        self._description = description

    def comprehensive(self):
        return '\n'.join(['{}: {}'.format(key.capitalize(), value)
                         for key, value in self.to_dict().items()])

    generic_types = ['Generic', 'Generics']
    report_types = ['Report', 'Reports']
    types = ['ADAF',
             'ADAFs',
             'Datasource',
             'Datasources',
             'Table',
             'Tables',
             'Text',
             'Texts',
             'Figure',
             'Figures',
             'Json',
             'Jsons'] + report_types + generic_types

    def to_dict(self):
        return OrderedDict([
            ('name', self._name),
            ('type', self._type),
            ('description', self._description)])

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def port_type(self):
        return self._type

    @port_type.setter
    def type(self, port_type):
        self._type = port_type

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        self._description = description


class NodeWizardPortsModel(QtCore.QAbstractListModel):
    def __init__(self, parent=None):
        super(NodeWizardPortsModel, self).__init__(parent)
        self._ports = []
        self.setSupportedDragActions(QtCore.Qt.CopyAction)

    def rowCount(self, modelindex):
        return len(self._ports)

    def columnCount(self, modelindex):
        return 1

    def data(self, modelindex, role):
        if not modelindex.isValid():
            return None

        row = modelindex.row()
        item = self._ports[row]

        if role == QtCore.Qt.DisplayRole:
            return item.name

        elif role == QtCore.Qt.ToolTipRole:
            return item.comprehensive()

        return None

    def port(self, modelindex):
        if not modelindex.isValid():
            return None
        return self._ports[modelindex.row()]

    def removeRows(self, row, count=1, parent=QtCore.QModelIndex()):
        curr_ports = self._ports
        new_ports = curr_ports[:row] + curr_ports[row + 1:]
        self.beginRemoveRows(QtCore.QModelIndex(), row, row + 1)
        self._ports = new_ports
        self.endRemoveRows()
        return len(new_ports) > len(curr_ports)

    def add(self, port):
        if (port.name == '' or
                any(p.name == port.name for p in self._ports)):
            return False
        count = len(self._ports)
        self.beginInsertRows(QtCore.QModelIndex(), count, count + 1)
        self._ports.append(port)
        self.endInsertRows()
        return True

    def update(self, model_index):
        self.beginRemoveRows(
            QtCore.QModelIndex(), model_index.row(), model_index.row())
        self.endRemoveRows()

    def ports(self):
        return self._ports

    def supportedDropActions(self):
        return QtCore.Qt.CopyAction

    def mimeData(self, model_index):
        mime_data = QtCore.QMimeData()
        mime_data.setData(
            MIME_TYPE, QtCore.QByteArray(model_index[0].row()))
        return mime_data

    def mimeTypes(self):
        return [MIME_TYPE]

    def dropMimeData(self, data, action, row, column, parent):
        from_row = int(data.data(MIME_TYPE))
        move_port = self._ports[from_row]
        del self._ports[from_row]
        self._ports.insert(row if from_row > row else row - 1, move_port)
        return True

    def flags(self, model_index):
        default = (
            QtCore.Qt.ItemIsSelectable |
            QtCore.Qt.ItemIsDragEnabled |
            QtCore.Qt.ItemIsEnabled)
        if model_index.isValid():
            return default
        return default | QtCore.Qt.ItemIsDropEnabled


class NodeWizardSummaryPage(QtGui.QWizardPage):
    def __init__(self, title, summary, parent=None):
        super(NodeWizardSummaryPage, self).__init__(parent)
        self._summary = summary
        self._parent = parent

        self._filename_lineedit = QtGui.QLineEdit()
        self._node_textedit = QtGui.QTextEdit()
        size = self._node_textedit.sizePolicy()
        size.setVerticalStretch(1)
        self._node_textedit.setSizePolicy(size)
        layout = QtGui.QFormLayout()

        # Set data.
        self._filename_lineedit.setReadOnly(True)
        self._node_textedit.setReadOnly(True)
        self.setTitle(title)

        # Layout.
        self.setStyleSheet("""QLineEdit { min-width: 40em }
                              QTextEdit { min-width: 40em }""")
        layout.addRow('Filename', self._filename_lineedit)
        layout.addRow('Code', self._node_textedit)
        self.setLayout(layout)
        layout.setFieldGrowthPolicy(QtGui.QFormLayout.ExpandingFieldsGrow)

    def initializePage(self):
        filename, node = self._parent.get_node()
        self._filename_lineedit.setText(filename)
        self._node_textedit.setHtml(
            highlight(node, PythonLexer(), HtmlFormatter(style='colorful',
                                                         full=True)))
        super(NodeWizardSummaryPage, self).initializePage()


class NodeWizardInfoPage(QtGui.QWizardPage):
    def __init__(self, title, info, tags, parent=None):
        super(NodeWizardInfoPage, self).__init__(parent)
        self._info = info
        self._tags = self._create_tags(tags)
        self._name_lineedit = ValidatingLineEdit(node_name_validator)
        self._author_lineedit = QtGui.QLineEdit()
        self._copyright_lineedit = QtGui.QLineEdit()
        self._version_lineedit = QtGui.QLineEdit()
        self._icon_lineedit = ValidatingLineEdit(icon_validator)
        self._description_textedit = QtGui.QTextEdit()
        self._tags_combo = QtGui.QComboBox()

        self._tags_combo.addItems(sorted(list(self._tags.keys())))
        layout = QtGui.QFormLayout()

        size = self._description_textedit.sizePolicy()
        size.setVerticalStretch(1)
        self._description_textedit.setSizePolicy(size)

        # Set data.
        self.setTitle(title)

        # Layout.
        self.setStyleSheet("""QLineEdit { min-width: 20em }
                              QTextEdit { min-width: 20em }""")

        layout.addRow('Name', self._name_lineedit)
        layout.addRow('Author', self._author_lineedit)
        layout.addRow('Copyright', self._copyright_lineedit)
        layout.addRow('Version', self._version_lineedit)
        layout.addRow('Icon', self._icon_lineedit)
        layout.addRow('Tags', self._tags_combo)
        layout.addRow('Description', self._description_textedit)
        self.setLayout(layout)
        layout.setFieldGrowthPolicy(QtGui.QFormLayout.ExpandingFieldsGrow)

        # Connect.
        self._name_lineedit.validated.connect(self.completeChanged)
        self._icon_lineedit.validated.connect(self.completeChanged)

    def result(self):
        return {'name': format_meta_data(self._name_lineedit.text()),
                'author': format_meta_data(self._author_lineedit.text()),
                'copyright': format_meta_data(self._copyright_lineedit.text()),
                'version': format_meta_data(self._version_lineedit.text()),
                'icon':
                    '/'.join(format_meta_data(
                        self._icon_lineedit.text()).split(os.path.sep)),
                'description':
                    format_meta_data(self._description_textedit.toPlainText()),
                'tags': self._tags[self._tags_combo.currentText()]}

    def isComplete(self):
        return self._name_lineedit.isValid() and self._icon_lineedit.isValid()

    def _create_tags(self, tags):
        tag_dict = {}
        for group in tags[4]:
            for tag in group[4]:
                if group[1] != 'Hidden' and group[1] != 'Example':
                    key = (group[3] if group[3] is not None else
                           group[1]) + '/' + (
                        tag[3] if tag[3] is not None else tag[1])
                    val = group[1] + '.' + tag[1]
                    tag_dict[key] = val
        return tag_dict


class NodeWizardPortsPage(QtGui.QWizardPage):
    def __init__(self, title, ports, parent=None):
        super(NodeWizardPortsPage, self).__init__(parent)
        self._ports = ports
        self._model = NodeWizardPortsModel()
        self._name_lineedit = ValidatingLineEdit(port_name_validator)
        self._type_combobox = QtGui.QComboBox()
        self._description_textedit = QtGui.QTextEdit()
        self._ports_list = PortList()

        self._add_update_button = QtGui.QPushButton('Add')
        remove_button = QtGui.QPushButton('Remove')
        layout = QtGui.QHBoxLayout()
        left_layout = QtGui.QFormLayout()
        right_layout = QtGui.QFormLayout()
        button_layout = QtGui.QHBoxLayout()
        left_layout.setFieldGrowthPolicy(
            QtGui.QFormLayout.ExpandingFieldsGrow)
        right_layout.setFieldGrowthPolicy(
            QtGui.QFormLayout.ExpandingFieldsGrow)
        size = self._description_textedit.sizePolicy()
        size.setVerticalStretch(1)
        self._description_textedit.setSizePolicy(size)

        # Set data.
        self.setTitle(title)
        self._ports_list.setModel(self._model)

        self._type_combobox.addItems(Port.types)
        self._type_combobox.setCurrentIndex(
            self._type_combobox.findText('Table'))
        # Workaround to get a fixed width
        self._type_combobox.setMaximumWidth(1)

        # Layout.
        self.setStyleSheet("""QLineEdit { min-width: 20em }
                              QTextEdit { min-width: 20em }
                              QComboBox { min-width: 20em }
                              QListView { min-width: 20em }""")

        button_layout.addWidget(self._add_update_button)
        button_layout.addWidget(remove_button)

        left_layout.addRow('Name', self._name_lineedit)
        left_layout.addRow('Type', self._type_combobox)
        left_layout.addRow('Description', self._description_textedit)

        right_layout.addRow('Ports', self._ports_list)
        right_layout.addRow('', button_layout)

        layout.addLayout(left_layout)
        layout.addLayout(right_layout)

        self.setLayout(layout)

        # Connect.
        self._add_update_button.clicked.connect(self.add)
        remove_button.clicked.connect(self.remove)
        self._ports_list.changed_selection.connect(self.select)
        self._name_lineedit.textChanged.connect(self.name_changed)
        self._ports_list.delete_pressed.connect(self.remove)

    def _clear_input(self):
        self._name_lineedit.setText('')
        self._description_textedit.setPlainText('')

    def add(self):
        if not self._name_lineedit.isValid():
            return
        port = Port(self._name_lineedit.text().strip(),
                    self._type_combobox.currentText(),
                    format_meta_data(self._description_textedit.toPlainText()))
        self._model.add(port)
        self._clear_input()

    def remove(self):
        selected = self._ports_list.selectedIndexes()
        if selected:
            for modelindex in reversed(selected):
                if modelindex.isValid():
                    self._model.removeRows(modelindex.row())

    def select(self):
        selected = self._ports_list.selectedIndexes()
        if not len(selected):
            self._clear_input()
        if len(selected) == 1:
            port = self._model.port(selected[0])
            self._name_lineedit.setText(port.name)
            self._description_textedit.setPlainText(port.description)
            self._type_combobox.setCurrentIndex(
                self._type_combobox.findText(port.port_type))
            self._add_update_button.setText('Update')
            self._add_update_button.clicked.disconnect()
            self._add_update_button.clicked.connect(self.update)
            self._add_update_button.setEnabled(True)
        else:
            self._add_update_button.setText('Add')
            self._add_update_button.clicked.disconnect()
            self._add_update_button.clicked.connect(self.add)

    def update(self):
        selected = self._ports_list.selectedIndexes()
        if len(selected) == 1:
            port = self._model.port(selected[0])
            port.name = self._name_lineedit.text()
            port.type = self._type_combobox.currentText()
            port.description = self._description_textedit.toPlainText()
            self._model.update(selected[0])

    def result(self):
        return [port.to_dict() for port in self._model.ports()]

    def name_changed(self):
        for port in self._model.ports():
            if self._name_lineedit.text() == port.name:
                self._add_update_button.setEnabled(False)
                return
        self._add_update_button.setEnabled(True)


class NodeWizardLibraryPage(QtGui.QWizardPage):
    def __init__(self, title, library, settings, app_core, parent=None):
        super(NodeWizardLibraryPage, self).__init__(parent)
        self._library = library
        self._settings = settings
        self._app_core = app_core
        self._library_index = {}
        self._node_identifiers = set()

        self._new_library = QtGui.QPushButton('New...')
        self._new_folder = QtGui.QPushButton('...')
        self._path_lineedit = QtGui.QLineEdit()
        self._prefix_lineedit = QtGui.QLineEdit()
        self._domain_lineedit = QtGui.QLineEdit()
        self._path_lineedit.setReadOnly(True)
        self._prefix_lineedit.setReadOnly(True)
        self._domain_lineedit.setReadOnly(True)
        self._new_folder.setEnabled(False)

        self._library_tree = QtGui.QTreeView()
        size = self._library_tree.sizePolicy()
        size.setVerticalStretch(1)
        self._library_tree.setSizePolicy(size)

        path_layout = QtGui.QHBoxLayout()
        path_layout.addWidget(self._path_lineedit)
        path_layout.addWidget(self._new_folder)

        layout = QtGui.QFormLayout()

        # Set data.
        self.setTitle(title)
        self._library_tree.setModel(library)
        self._selection_model = self._library_tree.selectionModel()

        self._index_libraries()

        # Layout.
        self.setStyleSheet("""QLineEdit { min-width: 30em }
                              QTreeView { min-width: 30em }""")
        layout.setContentsMargins(QtCore.QMargins())
        self._library_tree.setHeaderHidden(True)

        layout.addRow('', self._path_lineedit)
        layout.addRow('Create new Library',
                      self._new_library)
        layout.addRow('Library Identifier', self._domain_lineedit)
        layout.addRow('Library Path', self._prefix_lineedit)
        layout.addRow('Node Path', path_layout)
        layout.addRow('Library', self._library_tree)
        self.setLayout(layout)
        layout.setFieldGrowthPolicy(QtGui.QFormLayout.ExpandingFieldsGrow)

        # Connect.
        self._selection_model.selectionChanged.connect(self._selection_changed)
        self._new_library.clicked.connect(self._open_library_wizard)
        self._new_folder.clicked.connect(self._set_folder)

    def _open_library_wizard(self):
        wizard = librarywizard.LibraryWizard()
        wizard.exec_()
        if wizard.result() == QtGui.QDialog.Accepted:
            self._app_core.reload_node_library()
            self._library.update_model()
            self._library_tree.setModel(self._library)

    def _set_folder(self):
        base = self._prefix_lineedit.text()
        node = self._path_lineedit.text()
        path = os.path.normpath(os.path.join(base, node))
        dir_ = QtGui.QFileDialog.getExistingDirectory(
            self, 'Choose a directory', path)
        if dir_.startswith(base):
            dir_ = dir_.split(base)[1][1:]
            self._path_lineedit.setText(dir_)
        else:
            self._path_lineedit.setText(node)

    def isComplete(self):
        return all(len(item.text())
                   for item in [self._path_lineedit,
                                self._prefix_lineedit,
                                self._domain_lineedit])

    def _selection_changed(self, selected, deselected):
        self._new_folder.setEnabled(True)
        indexes = selected.indexes()

        if indexes:
            index = indexes[0]
            node_info = self._library.itemData(index)['node_info']
            self._index_libraries()

            if node_info is not None:
                path = node_info.path
                library_path, _ = self._library_index[path[0]]
            else:
                path = []
                while index.isValid():
                    path.append(self._library.data(index, QtCore.Qt.UserRole))
                    index = self._library.parent(index)
                path = list(reversed(path))

            library_path, _ = self._library_index[path[0]]
            ini_path = os.path.abspath(library_path + '/../' + LIBRARY_INI)
            self._path_lineedit.setText(os.path.sep.join(path))
            self._prefix_lineedit.setText(library_path)
            identifier = get_identifier_from_ini(self, ini_path)
            if not len(identifier):
                info = find_library_info(
                    os.path.abspath(library_path + '/../'))
                identifier = 'example'
                create_ini(ini_path, **info)
                if len(info['identifier']):
                    identifier = info['identifier']
                else:
                    QtGui.QMessageBox.warning(
                        self, 'Error', 'Error reading current library. '
                        'No ini file has been created and an example ID will '
                        'be used.')
                    identifier = 'example'
            self._domain_lineedit.setText(identifier)

            self.completeChanged.emit()

    def _index_libraries(self):
        for library in self._library._library_root.libraries:
            for node in library.nodes:
                self._library_index[node.path[0]] = (
                    uri_to_path(node.library),
                    '.'.join(node.node_identifier.split('.')[:2]))
                self._node_identifiers.add(node.node_identifier)

    def result(self):
        path = self._path_lineedit.text().strip()
        filename = os.path.sep.join(
            [self._prefix_lineedit.text(), path]).strip()
        nodeid_prefix = '{}.{}'.format(
            self._domain_lineedit.text(), path).strip()
        return {'filename_prefix': filename, 'nodeid_prefix': nodeid_prefix,
                'library_prefix': self._prefix_lineedit.text()}


class NodeWizard(SuperWizard):
    def __init__(self, library, settings, app_core, parent=None):
        super(NodeWizard, self).__init__('Node wizard', parent)
        self._library = library
        self._settings = settings
        info = {}
        in_ports = {}
        out_ports = {}
        summary = {}
        tags = app_core.get_library_dict()['tags']
        self._add_report = False

        self._info_page = NodeWizardInfoPage(
            'Base Information', info, tags, self)
        self._in_ports_page = NodeWizardPortsPage(
            'Input Ports', in_ports, self)
        self._out_ports_page = NodeWizardPortsPage(
            'Output Ports', out_ports, self)
        self._library_page = NodeWizardLibraryPage(
            'Library Location', library, settings, app_core, self)
        self._summary_page = NodeWizardSummaryPage(
            'Summary', summary, self)

        # Workaround to get all pages the same size
        self.setMinimumSize(700, 300)

        self.addPage(self._info_page)
        self.addPage(self._in_ports_page)
        self.addPage(self._out_ports_page)
        self.addPage(self._library_page)
        self.addPage(self._summary_page)

    def get_node(self):
        def get_port(type, name, description):
            custom_port = 'Port.Custom({port}, {description}, name={name})'
            regular_port = 'Port.{type}({description}, name={name})'
            if type in Port.types:
                if type in Port.generic_types:
                    port_name = ('<a>' if Port.generic_types[0] == type
                                 else '[<a>]')
                    return custom_port.format(
                        port=quote(port_name),
                        description=quote(description),
                        name=quote(name))
                elif type in Port.report_types:
                    self._add_report = True
                    return regular_port.format(
                        type=type,
                        description=quote(description),
                        name=quote(name)).replace('Port', 'report')
                else:
                    return regular_port.format(
                        type=type,
                        description=quote(description),
                        name=quote(name))
            else:
                raise NotImplementedError

        def quote(value):
            try:
                value = six.text_type(value)
            except UnicodeEncodeError:
                value = six.text_type(value.decode('utf8'))
            if value.find('\n') >= 0:
                return "'''{}'''".format(value)
            else:
                return "'{}'".format(value)

        info_result = self._info_page.result()
        in_ports_result = self._in_ports_page.result()
        out_ports_result = self._out_ports_page.result()
        library_result = self._library_page.result()

        name = info_result['name']
        author = info_result['author']
        copyright = info_result['copyright']
        version = info_result['version']
        icon = info_result['icon']
        description = info_result['description']
        tags = info_result['tags']
        tags = 'tags = Tags' + ('(Tag.' + tags + ')' if len(tags) else '()')

        class_name = format_python_string(name)

        ini_path = os.path.abspath(
            library_result['library_prefix'] + '/../' + LIBRARY_INI)
        identifier = get_identifier_from_ini(self, ini_path)
        nodeid = identifier + '.' + class_name.lower()

        filename = '{}{}node_{}.py'.format(
            library_result['filename_prefix'],
            os.path.sep,
            class_name.lower())

        inputs = 'Ports(\n        [{}])'.format(
            ',\n         '.join([get_port(**port)
                                for port in in_ports_result]))

        outputs = 'Ports(\n        [{}])'.format(
            ',\n         '.join([get_port(**port)
                                for port in out_ports_result]))

        header = """
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
from sympathy.api import node
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags"""

        report_import = (
            '\nfrom sympathy.api import report' if self._add_report else '')

        node = header + report_import + """


class {class_name}(node.Node):
    name = {name}
    author = {author}
    copyright = {copyright}
    version = {version}
    icon = {icon}
    description = {description}
    nodeid = {nodeid}
    {tags}

    inputs = {inputs}
    outputs = {outputs}

    def execute(self, node_context):
        raise NotImplementedError('Implement code here.')
""".format(name=quote(name),
           class_name=class_name,
           author=quote(author),
           copyright=quote(copyright),
           version=quote(version),
           icon=quote(icon),
           description=quote(description),
           nodeid=quote(nodeid),
           tags=tags,
           inputs=inputs,
           outputs=outputs)

        try:
            str(node)
        except UnicodeEncodeError:
            node = '# -*- coding: utf-8 -*-\n' + node

        return filename, node

    def done(self, result):
        if result == QtGui.QDialog.Accepted:
            filename, node = self.get_node()

            try:
                os.makedirs(os.path.dirname(filename))
            except OSError:
                pass

            with io.open(filename, 'w', encoding='utf8') as f:
                f.write(node)

        super(NodeWizard, self).done(result)
