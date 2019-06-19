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
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import sys
import re
import logging
import json
import os
import six

import PySide.QtCore as QtCore
import PySide.QtGui as QtGui

from sympathy.platform import workflow_converter
from sympathy.platform import version_support as vs
from . import flow_serialization
from . import settings

core_logger = logging.getLogger('core')
num_recent_flows = 15

# Text ordering options
FRONT = 'Bring to front'
FORWARD = 'Bring forward'
BACKWARD = 'Send backward'
BACK = 'Send to back'


class TermColors(object):
    """
    Available formatting constants are:

    FORE: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE.
    BACK: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE.
    Style: DIM, NORMAL, BRIGHT

    >>> print(RED('Hello World', style='BRIGHT'))
    Hello World
    """

    def __init__(self):
        try:
            # Terminal color support is optional.
            from colorama import init, Fore, Back, Style
            self.__initialized = False
            self.__init = init
            self.Fore = Fore
            self.Back = Back
            self.Style = Style
            self._grounds = {'FORE': self.Fore, 'BACK': self.Back}
        except ImportError:
            pass

    def initialize(self):
        if not self.__initialized:
            self.__initialized = True
            self.__init(wrap=False)

    def _color_text(self, text, color, ground, style):
        try:
            return '{} {} {} {} {}'.format(
                color, self.Style.__getattribute__(style), text,
                ground.RESET, self.Style.RESET_ALL)
        except Exception:
            return text

    def __getattr__(self, name):
        def inner(text, ground_str='FORE', style='NORMAL'):
            self.initialize()
            try:
                ground = self._grounds[ground_str]
                color = ground.__getattribute__(name.upper())
            except Exception:
                return text
            return self._color_text(text, color, ground, style)
        return inner


# HACK(alexander): This should not be exposed outside module.
TERM_COLORS = TermColors()


def color_functions(colors):
    return (TERM_COLORS.__getattr__(color) for color in colors)


COLORS = ('BLACK', 'RED', 'GREEN', 'YELLOW',
          'BLUE', 'MAGENTA', 'CYAN', 'WHITE')
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = color_functions(COLORS)


def hash_support(app, app_core):
    pass


def log_environ(app, app_core):
    pass


error_codes = {}


with open(os.path.join(vs.py_file_dir(__file__),
                       'Resources', 'error_codes.json'), 'r') as f:
    error_codes = json.load(f)


def return_value(description):
    return error_codes[description]['code']


def error_description(name):
    return error_codes[name]['description']


def print_error(error_name):
    core_logger.error('error: {}\n'.format(error_description(error_name)))


def format_output_exception(output):
    if output.exception.node_error:
        key = 'Error'
    else:
        key = 'Exception'
    data = output.exception.details
    if output.exception.path:
        data = 'Occurred in list index: {}\n{}'.format(
            output.exception.path, data)
    return key, six.text_type(data).strip()


def format_output_string(output):
    formatted_list = []
    if output.has_exception():
        key, data = format_output_exception(output)

        formatted_list.append(
            RED('{}'.format(data)))
    if len(output.stderr) > 0:
        formatted_list.append('stderr: {}'.format(output.stderr))
    if len(output.stdout) > 0:
        formatted_list.append('stdout: {}'.format(output.stdout))
    return '\n'.join(formatted_list)


def execution_error(output):
    errors = ('exception_string', 'stderr', 'exception_trace')
    return any((bool(output[k]) for k in errors))


class SaveCancelled(Exception):
    pass


def persistent_save_flow_to_file(flow_, default_filename=None):
    """
    Ask for a filename and try to save a flow. Keep trying until saving worked
    or until user cancelled.

    If the user cancels a SaveCancelled exception is raised. Otherwise the
    final filename is returned.

    If default_filename is set the method will try to save the flow there
    first without asking for a filename. If it fails it will go on to ask the
    user for another filename as usual.
    """
    status = False
    while not status:
        filename = default_filename or ask_for_filename(flow_)
        status = save_flow_to_file(flow_, filename)
        default_filename = None  # Don't try again with this filename.
    return filename


def save_flow_to_file(flow_, filename):
    """Save a flow to a file"""
    flow_dict = flow_.to_dict(stub=False)
    converter = workflow_converter.JsonToXml.from_dict(flow_dict)
    xml_data = converter.xml()
    try:
        with open(filename, 'wb') as flow_file:
            flow_file.write(vs.encode(xml_data, 'UTF-8'))
    except EnvironmentError:
        return False
    if not flow_.is_subflow() or flow_.is_linked:
        flow_.set_clean()
    if not flow_.is_subflow() or not flow_.is_linked:
        add_flow_to_recent_flows_list(filename)
    return True


def ask_for_filename(flow_):
    """
    Ask the user for a filename where a workflow should be saved.
    If the user cancels a SaveCancelled exception is raised.
    """
    # Find a good directory to present in the file dialog.
    flow_filename = flow_.root_or_linked_flow_filename
    if flow_filename:
        default_dir = os.path.dirname(flow_filename)
    else:
        default_dir = settings.instance()['default_folder']

    # Convert whitespaces to single space and remove trailing and leading
    # whitespace.
    default_filename = (
        re.sub(r'\s+', ' ', flow_.name, flags=re.UNICODE).strip()
        if len(flow_.name) else flow_filename)

    # If colon or any ascii control character is in the filename the Windows
    # save file dialog returns empty strings (the same as if the user cancelled
    # the dialog) without ever showing the dialog. To get around this remove
    # any such characters from the default filename.
    if sys.platform == 'win32':
        bad_chars = set(list(map(chr, range(32))) + [':'])
        default_filename = ''.join(
            c for c in default_filename if c not in bad_chars).strip()

    filename = QtGui.QFileDialog.getSaveFileName(
        None, 'Save flow', os.path.join(default_dir, default_filename),
        filter='Sympathy flow (*.syx)')[0]

    if len(filename) == 0:
        raise SaveCancelled()

    # Should never happen since filter is set:
    if not filename.endswith('.{}'.format(
            flow_.app_core.flow_suffix())):
        filename += '.{}'.format(flow_.app_core.flow_suffix())

    return filename


class UnsavedFilesDialog(QtGui.QDialog):
    """
    A dialog which shows a tree of flows and lets the user check those that
    should be saved.
    """

    def __init__(self, root_flows, include_root, discard, parent=None):
        super(UnsavedFilesDialog, self).__init__(parent)
        self._discard = False
        self._uuid_to_flow = {}

        if include_root:
            flows = root_flows
        else:
            flows = []
            for root_flow in root_flows:
                flows.extend(root_flow.shallow_subflows())

        self.setWindowTitle("Save changed flows?")
        text = QtGui.QLabel("Some flows or subflows have unsaved changes. "
                            "Would you like to save them?")

        self._flow_list = QtGui.QTreeWidget(self)
        self._flow_list.setColumnCount(3)
        self._flow_list.setHeaderLabels(
            ["Flow name", "Save?", "File"])
        dirty_uuids = set()
        for flow_ in flows:
            dirty_uuids.update(self._get_dirty_uuids(flow_))
        items = self._populate_model(flows, dirty_uuids=dirty_uuids)
        self._flow_list.addTopLevelItems(items)
        self._flow_list.expandAll()
        self._flow_list.resizeColumnToContents(0)

        if discard:
            self._buttons = QtGui.QDialogButtonBox(
                QtGui.QDialogButtonBox.Save |
                QtGui.QDialogButtonBox.Discard |
                QtGui.QDialogButtonBox.Cancel,
                parent=self)
        else:
            self._buttons = QtGui.QDialogButtonBox(
                QtGui.QDialogButtonBox.Save |
                QtGui.QDialogButtonBox.Cancel,
                parent=self)
        self._buttons.clicked.connect(self._clicked)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(text)
        layout.addWidget(self._flow_list)
        layout.addWidget(self._buttons)
        self.setLayout(layout)

    def _populate_model(self, flows, dirty_uuids, parent_item=None):
        """Populate the QTreeWidget item model using flows."""
        if parent_item is None:
            parent_item = self._flow_list

        items = []
        for flow_ in flows:
            if flow_.full_uuid in dirty_uuids:
                if not flow_.filename:
                    filename = None
                else:
                    filename = os.path.relpath(
                        flow_.filename, os.path.dirname(
                            flow_.root_or_linked_flow_filename))
                if flow_.is_linked or flow_.flow is None:
                    display_filename = filename or "<Not saved>"
                else:
                    display_filename = ""
                item = QtGui.QTreeWidgetItem(
                    parent_item, [flow_.display_name, '', display_filename])
                item.setFlags(
                    QtCore.Qt.ItemIsUserCheckable |
                    QtCore.Qt.ItemIsEnabled)
                item.setData(0, QtCore.Qt.UserRole, flow_.namespace_uuid())
                item.setData(2, QtCore.Qt.ToolTipRole, flow_.filename)
                self._uuid_to_flow[flow_.namespace_uuid()] = flow_
                if not flow_.is_clean() and (flow_.is_linked or
                                             flow_.flow is None):
                    item.setCheckState(1, QtCore.Qt.Checked)

                self._populate_model(
                    flow_.shallow_subflows(), dirty_uuids, item)
                items.append(item)
        return items

    def _get_dirty_uuids(self, root_flow):
        if root_flow.is_clean():
            dirty_subflows = []
        else:
            dirty_subflows = [root_flow]
        dirty_subflows.extend([f for f in root_flow.all_subflows()
                               if f.is_linked and not f.is_clean()])
        parent_flows = []
        for flow_ in dirty_subflows:
            while flow_ is not None:
                parent_flows.append(flow_)
                flow_ = flow_.flow
        return set([f.full_uuid for f in parent_flows + dirty_subflows])

    def _clicked(self, button):
        """Handle when the user clicks a dialog button (Save/Cancel)."""
        button = self._buttons.standardButton(button)
        if button == QtGui.QDialogButtonBox.StandardButton.Save:
            self.accept()
        elif button == QtGui.QDialogButtonBox.StandardButton.Discard:
            self._discard = True
            self.accept()
        elif button == QtGui.QDialogButtonBox.StandardButton.Cancel:
            self.reject()

    def selected_flows(self):
        """Return a set with the flows that were selected to be saved."""
        if self._discard:
            return []

        def item_to_flow(item):
            uuid = item.data(0, QtCore.Qt.UserRole)
            return self._uuid_to_flow[uuid]

        def item_to_flows(item):
            flows = set()
            if item.checkState(1) == QtCore.Qt.Checked:
                flows.add(item_to_flow(item))
            for i in range(item.childCount()):
                child_item = item.child(i)
                flows.update(item_to_flows(child_item))
            return flows

        flows = set()
        for i in range(self._flow_list.topLevelItemCount()):
            item = self._flow_list.topLevelItem(i)
            flows.update(item_to_flows(item))
        return flows


def ask_about_saving_flows(root_flows, include_root=False, discard=False):
    """
    Show a dialog to let the user choose to save or discard any changes in the
    flows in root_flows or their subflows.

    If there are no unsaved changes in any of the flows in root_flows
    (including subflows), no dialog is shown.

    Parameters
    ----------
    root_flows : list of flows
    include_root : bool, optional
        If True, both the flows in root_flows and all their subflows will be
        considered. If False, only the subflows are checked.
    discard : bool, optional
        If True, adds a button that lets the user discard all the flows. This
        is only needed when closing a flow tab or quiting the application, and
        the button can have a text like "Quit without saving" on some
        platforms.
    """
    if include_root:
        flows = root_flows
    else:
        flows = []
        for root_flow in root_flows:
            flows.extend(root_flow.shallow_subflows())

    if all([f.subflows_are_clean() for f in flows]):
        return

    dialog = UnsavedFilesDialog(root_flows, include_root, discard)
    result = dialog.exec_()
    if result == QtGui.QDialog.Accepted:
        flows = dialog.selected_flows()
        for flow_ in flows:
            persistent_save_flow_to_file(flow_, flow_.filename or None)
    elif result == QtGui.QDialog.Rejected:
        raise SaveCancelled()


def read_flow_from_file(app_core, filename, flows=None,
                        open_window=lambda new_flow: None):
    """
    Read flow with given file name.

    flows is a list to which the new flow gets appended. open_window is a
    function which takes the new flow and opens it. This is intended for GUI
    mode, the default is a function that does nothing to the flow argument.
    """
    filename = vs.fs_decode(filename)
    cwd = six.moves.getcwd()
    validate_enabled = app_core.validate_enabled()
    app_core.set_validate_enabled(False)
    try:
        deserializer = flow_serialization.FlowDeserializer(app_core)
        deserializer.load_xml_file(filename)
        if not deserializer.is_valid():
            core_logger.critical('Failed to load {}'.format(filename))

        new_flow = app_core.create_flow(
            deserializer.to_dict()['uuid'])
        if flows is not None:
            flows.append(new_flow)
        new_flow.filename = os.path.abspath(filename)
        os.chdir(os.path.dirname(new_flow.filename))
        deserializer.build_flow(new_flow)
        open_window(new_flow)
    except Exception:
        os.chdir(cwd)
        raise
    finally:
        app_core.set_validate_enabled(validate_enabled)
    return new_flow


def add_flow_to_recent_flows_list(filename):
    """Helper: Update the recent flows list."""
    if filename == "":
        core_logger.debug("Not adding empty string to recent files.")
        return
    elif os.path.isdir(filename):
        core_logger.debug("Not adding directory {} to recent files."
                          .format(filename))
        return

    recent_flows = settings.instance()['Gui/recent_flows']
    recent_flows.insert(0, os.path.abspath(filename))
    recent_flows = [x for x in recent_flows if x]
    # Uniquify recent flows
    seen = set()
    recent_flows = [x for x in recent_flows
                    if (os.path.normpath(x) not in seen and
                        not seen.add(os.path.normpath(x)))][:num_recent_flows]

    settings.instance()['Gui/recent_flows'] = recent_flows
