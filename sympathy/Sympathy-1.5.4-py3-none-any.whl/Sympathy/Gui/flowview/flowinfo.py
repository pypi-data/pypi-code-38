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
import json
import cgi
import os.path

import PySide.QtGui as QtGui
import PySide.QtCore as QtCore

from .types import get_label
from sympathy.utils import uuid_generator
from sympathy.utils import prim
from sympathy.platform.widget_library import (PathListWidget, PathLineEdit,
                                              ExpandingTextEdit)
from Gui import user_commands
from Gui import preferences


def _nativepath_or_empty(path):
    if path:
        path = prim.nativepath(path)
    return path


def show_info(model):
    dialog = FlowInfo(model, stub=False)
    result = dialog.exec_()
    cmds = []
    if result == QtGui.QDialog.Accepted:
        flow_info = dialog.get_flow_info()
        if model.is_linked:
            # Handle link label changes separately since they belong to a
            # different flow.
            link_label = flow_info.pop('label')
            if link_label != model.name:
                cmds.append(user_commands.EditNodeLabelCommand(
                    model, model.name, link_label))
        old_flow_info = model.get_flow_info()
        if any(old_flow_info[k] != flow_info[k] for k in flow_info):
            cmds.append(user_commands.SetFlowInfo(model, flow_info))
        libraries = dialog.get_libraries()
        pythonpaths = dialog.get_pythonpaths()
        if (libraries != model.library_paths() or
                pythonpaths != model.python_paths()):
            cmds.append(user_commands.SetFlowLibraries(
                model, libraries, pythonpaths))

        if len(cmds) > 1:
            model.undo_stack().beginMacro('Changing flow properties')
        for cmd in cmds:
            model.undo_stack().push(cmd)
        if len(cmds) > 1:
            model.undo_stack().endMacro()


def pre(text):
    return u'<pre>{}</pre>'.format(cgi.escape(text, quote=True))


class LinkInfoTab(QtGui.QWidget):
    def __init__(self, flow_model, stub, parent=None):
        super(LinkInfoTab, self).__init__(parent)

        layout = QtGui.QFormLayout()
        layout.setFieldGrowthPolicy(QtGui.QFormLayout.ExpandingFieldsGrow)

        # Set up editable flow info.
        self._label_edit = QtGui.QLineEdit(flow_model.link_label)
        layout.addRow('Link label', self._label_edit)

        layout.addRow('Filename', get_label(
            _nativepath_or_empty(flow_model.root_or_linked_flow_filename)))

        if flow_model.is_linked and not flow_model.node_identifier:
            layout.addRow(
                'Path from parent flow', get_label(
                    _nativepath_or_empty(flow_model.source_uri)))
        self.setLayout(layout)

    @property
    def label(self):
        return self._label_edit.text()


class GeneralInfoTab(QtGui.QWidget):
    def __init__(self, flow_model, stub, parent=None):
        super(GeneralInfoTab, self).__init__(parent)
        self._flow = flow_model
        self._tag_key_dict = {}

        layout = QtGui.QFormLayout()
        layout.setFieldGrowthPolicy(QtGui.QFormLayout.ExpandingFieldsGrow)

        # Set up editable flow info.
        flow_info = flow_model.get_flow_info()
        if flow_model.is_linked:
            label = flow_info['source_label']
        else:
            label = flow_info['label']
        self._label_edit = QtGui.QLineEdit(label)
        layout.addRow('Label', self._label_edit)
        self._description_edit = QtGui.QLineEdit(flow_info['description'])
        layout.addRow('Description', self._description_edit)
        self._author_edit = QtGui.QLineEdit(flow_info['author'])
        layout.addRow('Author', self._author_edit)
        self._version_edit = QtGui.QLineEdit(flow_info['version'])
        layout.addRow('Version', self._version_edit)
        self._copyright_edit = QtGui.QLineEdit(flow_info['copyright'])
        layout.addRow('Copyright', self._copyright_edit)
        self._min_version_edit = QtGui.QLineEdit(flow_info['min_version'])
        self._min_version_edit.setPlaceholderText('E.g. 1.2.3')
        self._min_version_validator = QtGui.QRegExpValidator(
            QtCore.QRegExp(r"[0-9]+\.[0-9]+\.[0-9]+"))
        self._min_version_edit.setValidator(self._min_version_validator)
        layout.addRow('Minimum Sympathy version', self._min_version_edit)

        def flatten(lists):
            return [i for list in lists for i in list]

        def list_tags(tags):
            if tags.term:
                return [tags]
            return [list_tags(tag) for tag in tags]

        def build_tags(path, tags):
            if tags.term:
                return '/'.join(path)
            else:
                return [build_tags(path + [tag.name], tag) for tag in tags]

        def build_tags_keys(path, tags):
            if tags.term:
                return '.'.join(path)
            else:
                return [build_tags_keys(path + [tag.key], tag) for tag in tags]

        tag_list = flatten(
            build_tags([], self._flow.app_core.library_root().tags.root))

        self._tag_key_dict = dict(zip(flatten(
            build_tags_keys([], self._flow.app_core.library_root().tags.root)),
                                     tag_list))

        self._tag_combo = QtGui.QComboBox()
        self._tag_combo.addItems(tag_list)

        layout.addRow('Tag', self._tag_combo)
        tag_idx = self._tag_combo.findText(
            self._tag_key_dict.get(flow_info['tag'], ''))
        self._tag_combo.setCurrentIndex(tag_idx)

        self._identifier_edit = QtGui.QLineEdit(flow_info['identifier'])
        layout.addRow('Identifier', self._identifier_edit)

        layout.addRow('Filename', get_label(
            _nativepath_or_empty(flow_model.root_or_linked_flow_filename)))

        if not _is_file_flow(flow_model):
            self._identifier_edit.setEnabled(False)
            self._tag_combo.setEnabled(False)

        self._icon_edit = PathLineEdit(
            self._flow.icon_filename,
            root_path=os.path.dirname(self._flow.root_or_linked_flow_filename),
            placeholder_text='SVG filename',
            filter='SVG icon files (*.svg);;All files (*.*)',
            default_relative=True)

        layout.addRow('Icon', self._icon_edit)

        if not self._flow.root_or_linked_flow_filename:
            self._icon_edit.setEnabled(False)

        # Show different UUIDs depending on whether subflow is linked and
        # whether we are showing stub or full flow.
        namespace_uuid, item_uuid = uuid_generator.split_uuid(
            flow_model.full_uuid)
        layout.addRow('Namespace UUID', get_label(pre(namespace_uuid)))
        if flow_model.is_linked:
            if stub:
                layout.addRow('UUID', get_label(pre(item_uuid)))
                layout.addRow(
                    'Source UUID', get_label(pre(flow_model.source_uuid)))
            else:
                layout.addRow('UUID', get_label(pre(flow_model.source_uuid)))
        else:
            layout.addRow('UUID', get_label(pre(item_uuid)))
        layout.addRow(
            'State', get_label(pre(flow_model.state_string())))

        self.setLayout(layout)

    @property
    def label(self):
        return self._label_edit.text()

    @property
    def description(self):
        return self._description_edit.text()

    @property
    def author(self):
        return self._author_edit.text()

    @property
    def version(self):
        return self._version_edit.text()

    @property
    def min_version(self):
        return self._min_version_edit.text()

    @property
    def copyright(self):
        return self._copyright_edit.text()

    @property
    def icon(self):
        return self._icon_edit.path()

    @property
    def tag(self):
        return dict(zip(self._tag_key_dict.values(),
                        self._tag_key_dict.keys())).get(
            self._tag_combo.currentText(), '')

    @property
    def identifier(self):
        return self._identifier_edit.text()


def _is_file_flow(flow):
    return (flow.root_or_linked_flow_filename and
            flow.root_or_linked_flow() is flow)


class LibrariesTab(QtGui.QWidget):
    def __init__(self, flow_model, parent=None):
        super(LibrariesTab, self).__init__(parent)
        self._flow = flow_model
        self._library_widget = PathListWidget(
            flow_model.library_paths(),
            recent=preferences.get_recent_libs(),
            root_path=os.path.dirname(self._flow.root_or_linked_flow_filename),
            default_relative=True)
        self._pythonpaths_widget = PathListWidget(
            flow_model.python_paths(),
            root_path=os.path.dirname(self._flow.root_or_linked_flow_filename),
            default_relative=True)

        if not _is_file_flow(self._flow):
            self._library_widget.setEnabled(False)
            self._pythonpaths_widget.setEnabled(False)

        layout = QtGui.QFormLayout()
        layout.setFieldGrowthPolicy(QtGui.QFormLayout.ExpandingFieldsGrow)
        layout.addRow('Workflow libraries', self._library_widget)
        layout.addRow('Python paths', self._pythonpaths_widget)
        self.setLayout(layout)

    @property
    def library_paths(self):
        return self._library_widget.paths()

    @property
    def recent_library_paths(self):
        return self._library_widget.recent()

    @property
    def python_paths(self):
        return self._pythonpaths_widget.paths()


class EnvironmentTab(QtGui.QWidget):
    root_msg = ('Note: Only the root flow and linked flows can have '
                'workflow environment variables')

    def __init__(self, flow_model, parent=None):
        super(EnvironmentTab, self).__init__(parent)
        self._flow = flow_model
        self._root = flow_model.root_or_linked_flow()
        layout = QtGui.QVBoxLayout()
        self._env_widget = preferences.ModifyEnvironmentWidget(self)

        if self._flow is not self._root:
            self._env_widget.setEnabled(False)
            layout.addWidget(QtGui.QLabel(self.root_msg))

        layout.addWidget(self._env_widget)
        self._old_env = self._flow.environment
        self._env_widget.set_variables(self._old_env)
        self.setLayout(layout)
        self._env_widget.resize_to_content()

    def apply(self):
        workflow_env_vars = self._env_widget.variables()
        if workflow_env_vars != self._old_env:
            assert self._flow is self._root, self.root_msg
            cmd = user_commands.EditWorkflowEnvironment(
                self._flow,
                workflow_env_vars,
                self._old_env)

            self._flow.undo_stack().push(cmd)


class OtherInfoTab(QtGui.QWidget):
    def __init__(self, flow_model, stub, parent=None):
        super(OtherInfoTab, self).__init__(parent)

        layout = QtGui.QFormLayout()
        layout.setFieldGrowthPolicy(QtGui.QFormLayout.ExpandingFieldsGrow)

        pretty_graph = flow_model.print_graph()
        graph_view = ExpandingTextEdit(pre(pretty_graph), self)
        layout.addRow('Graph', graph_view)

        full_json = json.dumps(flow_model.to_dict(stub=stub), indent=2)
        json_view = ExpandingTextEdit(pre(full_json), self)
        layout.addRow('Full JSON', json_view)

        self.setLayout(layout)


class ParametersTab(QtGui.QWidget):
    def __init__(self, flow_model, parent=None):
        super(ParametersTab, self).__init__(parent)

        layout = QtGui.QFormLayout()
        layout.setFieldGrowthPolicy(QtGui.QFormLayout.ExpandingFieldsGrow)

        aggregation = json.dumps(flow_model.aggregation_settings, indent=2)
        aggregation_view = ExpandingTextEdit(pre(aggregation), self)
        layout.addRow('Aggregation Settings', aggregation_view)

        overrides = json.dumps(flow_model.override_parameters, indent=2)
        overrides_view = ExpandingTextEdit(pre(overrides), self)
        layout.addRow('Parameter Overrides', overrides_view)

        self.setLayout(layout)


class FlowInfo(QtGui.QDialog):
    """Show and allow changing basic flow information."""

    def __init__(self, flow_model, stub, parent=None, flags=0):
        super(FlowInfo, self).__init__(parent, flags)
        self._is_linked = flow_model.is_linked

        self.setWindowTitle(u'Properties {}'.format(
            prim.format_display_string(flow_model.name)))
        self._main_layout = QtGui.QVBoxLayout()

        if self._is_linked:
            self._link_info = LinkInfoTab(flow_model, stub, parent)

        self._general_info = GeneralInfoTab(flow_model, stub, parent)
        if flow_model.library_node:
            self._general_info.setEnabled(False)

        self._libraries_tab = LibrariesTab(flow_model, parent)
        self._environment_tab = EnvironmentTab(flow_model, parent)

        tab_widget = QtGui.QTabWidget(self)
        tab_widget.addTab(self._general_info, 'General')
        if self._is_linked:
            tab_widget.addTab(self._link_info, 'Link')
        tab_widget.addTab(self._libraries_tab, 'Libraries')

        tab_widget.addTab(self._environment_tab, 'Environment variables')
        tab_widget.addTab(ParametersTab(flow_model, parent), 'Parameters')
        tab_widget.addTab(OtherInfoTab(flow_model, stub, parent), 'Advanced')

        self._main_layout.addWidget(tab_widget)
        button_box = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.apply)
        button_box.rejected.connect(self.reject)
        self._main_layout.addWidget(button_box)
        self.setLayout(self._main_layout)

    def apply(self):
        self._environment_tab.apply()
        self.accept()
        preferences.set_recent_libs(
            self._libraries_tab.recent_library_paths)

    def get_flow_info(self):
        """Return a dictionary with the (possibly updated) flow info."""
        flow_info = {
            'label': self._general_info.label,
            'description': self._general_info.description,
            'author': self._general_info.author,
            'version': self._general_info.version,
            'min_version': self._general_info.min_version,
            'copyright': self._general_info.copyright,
            'icon_filename': self._general_info.icon,
            'tag': self._general_info.tag,
            'identifier': self._general_info.identifier}
        if self._is_linked:
            flow_info.update({
                'source_label': self._general_info.label,
                'label': self._link_info.label})
        return flow_info

    def get_libraries(self):
        """Return a list with the (possibly updated) workflow libraries."""
        return self._libraries_tab.library_paths

    def get_pythonpaths(self):
        """Return a list with the (possibly updated) workflow python paths."""
        return self._libraries_tab.python_paths
