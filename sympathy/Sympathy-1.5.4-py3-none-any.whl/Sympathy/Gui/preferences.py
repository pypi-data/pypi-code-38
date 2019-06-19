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
import copy
import distutils.spawn
import collections
import six
import pygments.styles
import PySide.QtCore as QtCore
import PySide.QtGui as QtGui
from sympathy.platform import version_support as vs
from sympathy.platform.widget_library import PathListWidget
from . import settings
from Gui.environment_variables import instance as env_instance
from .flowview import grid
num_recent_libs = 15
ENV = env_instance()

# Determines the order in which actions are applied
A_ENV, A_LIBRARY_PATH, A_LIBRARY_RELOAD, A_LIBRARY_TYPE, A_LIBRARY_HIGHLIGHTER = range(5)  # noqa


class PreferencesWidgetInterface(QtCore.QObject):
    """docstring for PreferencesWidgetInterface"""

    def __init__(self, parent):
        super(PreferencesWidgetInterface, self).__init__(parent)
        self._path = ''
        self._widget = None
        self._menu_manager = None

    def apply_preferences(self):
        raise NotImplementedError('Not implemented for interface')

    def initialize(self, app_core, current_flow):
        self._app_core = app_core
        self._current_flow = current_flow

    def path(self):
        return self._path

    def widget(self):
        return self._widget

    def create_layout(self):
        layout = QtGui.QFormLayout()
        layout.setFieldGrowthPolicy(QtGui.QFormLayout.ExpandingFieldsGrow)
        layout.setFormAlignment(QtCore.Qt.AlignLeft)
        layout.setLabelAlignment(QtCore.Qt.AlignVCenter)
        layout.setVerticalSpacing(15)
        return layout

    def centered_label(self, string):
        label = QtGui.QLabel(string)
        label.setSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        return label

    def set_menu_manager(self, menu_manager):
        self._menu_manager = menu_manager


class PreferencesItem(QtGui.QStandardItem):
    """docstring for PreferencesItem"""

    def __init__(self, title):
        super(PreferencesItem, self).__init__(title)
        self._widget = None

    @property
    def widget(self):
        return self._widget

    @widget.setter
    def widget(self, value):
        self._widget = value


class PreferencesNavigator(QtGui.QTreeView):
    """docstring for PreferencesNavigator"""

    preferences_widget_change = QtCore.Signal(PreferencesWidgetInterface)

    def __init__(self, parent=None):
        super(PreferencesNavigator, self).__init__(parent)
        self._model = QtGui.QStandardItemModel()
        self.setModel(self._model)
        self.setHeaderHidden(True)
        model = self.selectionModel()
        model.selectionChanged[
            QtGui.QItemSelection, QtGui.QItemSelection].connect(
            self.leaf_selected)

    @QtCore.Slot(QtGui.QItemSelection, QtGui.QItemSelection)
    def leaf_selected(self, selected_item, deselected_item):
        self.preferences_widget_change.emit(self._model.itemFromIndex(
            selected_item.indexes()[0]).widget)

    def _get_item(self, title, default_item):
        matches = self._model.findItems(
            title, QtCore.Qt.MatchExactly | QtCore.Qt.MatchRecursive)
        if len(matches) > 0:
            return True, matches[0]
        else:
            return False, default_item

    def add_widget(self, widget):
        path = widget.path().split('/')
        root_exists = False
        previous = None
        root = None
        item = None
        for title in path:
            item_found, item = self._get_item(title, PreferencesItem(title))
            if previous:
                if not item_found:
                    item.setFlags(QtCore.Qt.NoItemFlags)
                    previous.appendRow(item)
            else:
                root = item
                root_exists = item_found
            previous = item
        item.widget = widget
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        if not root_exists:
            self._model.appendRow(root)
            if root is not item:
                root.setFlags(QtCore.Qt.NoItemFlags)


class PreferencesDialog(QtGui.QDialog):
    """docstring for PreferencesDialog"""

    def __init__(self, app_core, current_flow, menu_manager,
                 preference_widgets=None, parent=None):
        super(PreferencesDialog, self).__init__(parent)
        self.setWindowTitle('Preferences')
        self._menu_manager = menu_manager
        self._app_core = app_core
        self._current_flow = current_flow
        self._preference_widgets = preference_widgets or []
        self._widgets = []
        self._imp_to_vis_widget = {}
        self._pane = None
        self._tree_widget = None
        self.setMinimumSize(QtCore.QSize(825, 425))
        self.setMaximumSize(QtCore.QSize(2000, 2000))
        self._init()

    def _init(self):
        self._pane = QtGui.QStackedWidget()
        self._pane.setMinimumSize(QtCore.QSize(600, 275))
        self._pane.setMaximumSize(QtCore.QSize(1900, 1900))
        self._tree_widget = PreferencesNavigator()
        self._tree_widget.setMinimumSize(QtCore.QSize(150, 275))
        self._tree_widget.setMaximumSize(QtCore.QSize(150, 1900))
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self._tree_widget)
        ok_cancel_layout = QtGui.QVBoxLayout()
        ok_cancel_buttons = QtGui.QDialogButtonBox()
        ok_cancel_buttons.addButton(QtGui.QDialogButtonBox.Ok)
        ok_cancel_buttons.addButton(QtGui.QDialogButtonBox.Cancel)
        ok_cancel_buttons.accepted.connect(self.accept)
        ok_cancel_buttons.rejected.connect(self.reject)
        ok_cancel_layout.addItem(layout)
        ok_cancel_layout.addWidget(ok_cancel_buttons)
        for widget in self._preference_widgets:
            self._add_widget(widget)
            widget.set_menu_manager(self._menu_manager)
        layout.addWidget(self._pane, 1)
        self.setLayout(ok_cancel_layout)
        self._tree_widget.preferences_widget_change[
            PreferencesWidgetInterface].connect(self.change_widget)
        self.accepted.connect(self.apply_preferences)

    def _add_widget(self, widget):
        widget.initialize(self._app_core, self._current_flow)
        self._widgets.append(widget)
        container = QtGui.QScrollArea()
        container.setWidgetResizable(True)
        container.setWidget(widget.widget())
        container.ensureWidgetVisible(widget.widget())
        self._pane.addWidget(container)
        self._tree_widget.add_widget(widget)
        self._imp_to_vis_widget[widget.widget()] = container

    @QtCore.Slot(PreferencesWidgetInterface)
    def change_widget(self, widget):
        self._pane.setCurrentWidget(self._imp_to_vis_widget[widget.widget()])

    @QtCore.Slot()
    def apply_preferences(self):
        actions = []
        for widget in self._widgets:
            actions.extend(widget.apply_preferences() or [])
        settings.instance().sync()

        # Each action_id is performed only once.
        for action_id, action in sorted(
                collections.OrderedDict(actions).items()):
            action()


class GeneralSettingsWidget(PreferencesWidgetInterface):
    """General settings"""

    def __init__(self, parent=None):
        super(GeneralSettingsWidget, self).__init__(parent)
        self._available_themes = None
        self._path = 'General'

    def initialize(self, app_core, current_flow):
        super(GeneralSettingsWidget, self).initialize(app_core, current_flow)
        self._widget = QtGui.QWidget()
        settings_ = settings.instance()

        if self._available_themes is None:
            self._available_themes = sorted(pygments.styles.get_all_styles())

        self._layout = self.create_layout()
        self._init_snap(settings_)
        self._init_gui_settings(settings_)

    def _init_snap(self, settings_):
        self._snap_type = QtGui.QComboBox()
        self._grid_spacing = QtGui.QSpinBox()
        self._grid_spacing.setMaximum(999999)

        choices = ['Nothing'] + sorted(list(grid.SNAP_RESOLUTIONS.keys()))
        self._snap_type.addItems(choices)
        try:
            self._snap_type.setCurrentIndex(
                choices.index(settings_['Gui/snap_type']))
        except ValueError:
            self._snap_type.setCurrentIndex(0)

        validator = QtGui.QDoubleValidator()
        validator.setRange(0.0, 200.0, 1)
        self._grid_spacing.setValue(settings_['Gui/grid_spacing'])

        self._layout.addRow('Snap nodes to', self._snap_type)
        self._layout.addRow(
            'Grid spacing (a node is appx. 50)', self._grid_spacing)

    def _init_gui_settings(self, settings_):
        self._code_editor_theme = QtGui.QComboBox()
        self._code_editor_theme.addItems(self._available_themes)
        try:
            self._code_editor_theme.setCurrentIndex(
                self._available_themes.index(
                    settings_['Gui/code_editor_theme']))
        except ValueError:
            self._code_editor_theme.setCurrentIndex(
                self._available_themes.index('default'))
        self._use_system_editor = QtGui.QCheckBox()
        self._use_system_editor.setChecked(settings_['Gui/system_editor'])
        self._ask_for_save = QtGui.QCheckBox()
        self._ask_for_save.setChecked(settings_['ask_for_save'])
        self._save_session = QtGui.QCheckBox()
        self._save_session.setChecked(settings_['save_session'])
        self._nodeconfig_confirm_cancel = QtGui.QCheckBox()
        self._nodeconfig_confirm_cancel.setChecked(
            settings_['Gui/nodeconfig_confirm_cancel'])
        self._new_flow_on_start = QtGui.QCheckBox()
        self._new_flow_on_start.setChecked(settings_['new_flow_on_start'])

        self._docking = QtGui.QComboBox()
        self._docking.addItems(['Detachable', 'Movable', 'Locked'])
        dock_value = settings_['Gui/docking_enabled']
        dock_index = self._docking.findText(dock_value)
        dock_index = dock_index if dock_index != -1 else 0
        self._docking.setCurrentIndex(dock_index)

        self._conn_shape = QtGui.QComboBox()
        self._conn_shape.addItems(['Spline', 'Line'])
        conn_shape_value = settings_['Gui/flow_connection_shape']
        conn_shape_index = self._conn_shape.findText(conn_shape_value)
        self._conn_shape.setCurrentIndex(
            conn_shape_index if conn_shape_index != -1 else 0)

        self._clear_recent = QtGui.QPushButton('Clear recent flow list')
        self._clear_recent.setMaximumWidth(150)
        self._clear_recent.clicked.connect(self.clear_recent)

        self._layout.addRow('Code editor theme', self._code_editor_theme)
        self._layout.addRow('Use system text editor', self._use_system_editor)
        self._layout.addRow('Ask about saving flows on quit/close',
                            self._ask_for_save)
        self._layout.addRow('Save session (all open flows) on quit',
                            self._save_session)
        self._layout.addRow('Confirm cancel on node configurations',
                            self._nodeconfig_confirm_cancel)
        self._layout.addRow('Open an empty flow on program start',
                            self._new_flow_on_start)
        self._layout.addRow('View layout', self._docking)

        if settings_['Gui/experimental']:
            self._layout.addRow('Connection shape', self._conn_shape)

        self._layout.addRow(self._clear_recent)
        self._widget.setLayout(self._layout)

    def apply_preferences(self):
        result = []
        settings_ = settings.instance()

        snap_type = self._snap_type.currentText()
        settings_['Gui/snap_type'] = snap_type
        grid.instance().reload_settings()
        grid_spacing = float(self._grid_spacing.text())
        settings_['Gui/grid_spacing'] = grid_spacing
        settings_['Gui/system_editor'] = self._use_system_editor.isChecked()
        settings_['ask_for_save'] = self._ask_for_save.isChecked()
        settings_['save_session'] = self._save_session.isChecked()
        settings_['Gui/nodeconfig_confirm_cancel'] = (
            self._nodeconfig_confirm_cancel.isChecked())
        settings_['new_flow_on_start'] = self._new_flow_on_start.isChecked()
        settings_['Gui/code_editor_theme'] = (
            self._code_editor_theme.currentText())
        settings_['Gui/docking_enabled'] = self._docking.currentText()
        settings_['Gui/flow_connection_shape'] = self._conn_shape.currentText()
        return result

    def clear_recent(self):
        settings.instance()['Python/recent_library_path'] = []
        settings.instance()['Gui/recent_flows'] = []
        if self._menu_manager is not None:
            self._menu_manager.update_menus()


def get_recent_libs():
    settings_ = settings.instance()
    return settings_['Python/recent_library_path']


def set_recent_libs(recent_libs):
    settings_ = settings.instance()
    settings_['Python/recent_library_path'] = recent_libs[
        :num_recent_libs]


class LibrariesSettingsWidget(PreferencesWidgetInterface):
    """Settings concerning the node libraries"""

    library_path_changed = QtCore.Signal()

    def __init__(self, parent=None):
        super(LibrariesSettingsWidget, self).__init__(parent)
        self._path = 'Node Libraries'

    def initialize(self, app_core, current_flow):
        super(LibrariesSettingsWidget, self).initialize(app_core, current_flow)
        self._widget = QtGui.QWidget()
        settings_ = settings.instance()
        self._layout = self.create_layout()
        self._initial_library = settings_['Python/library_path']
        self._initial_recent = get_recent_libs()
        self._path_list = PathListWidget(
            self._initial_library, root_path=settings_['install_folder'],
            recent=self._initial_recent, default_relative=False,
            parent=self._widget)
        self._layout.addRow(
            self.centered_label('Node library'), self._path_list)
        self._widget.setLayout(self._layout)

    def apply_preferences(self):
        result = []
        settings_ = settings.instance()
        lib_path = self._path_list.paths()

        if lib_path != self._initial_library:
            settings_['Python/library_path'] = lib_path
            set_recent_libs(self._path_list.recent())

            result.append(
                (A_LIBRARY_RELOAD,
                 self._app_core.reload_node_library))
            result.append(
                (A_LIBRARY_PATH,
                 self.library_path_changed.emit))
        return result


class PythonSettingsWidget(PreferencesWidgetInterface):
    """Settings concerning python"""

    def __init__(self, parent=None):
        super(PythonSettingsWidget, self).__init__(parent)
        self._path = 'Python'

    def initialize(self, app_core, current_flow):
        super(PythonSettingsWidget, self).initialize(app_core, current_flow)
        self._widget = QtGui.QWidget()
        settings_ = settings.instance()
        self._layout = self.create_layout()
        self._initial_python_path = settings_['Python/python_path']
        self._path_list = PathListWidget(
            self._initial_python_path,
            root_path=settings_['install_folder'], parent=self._widget)
        self._layout.addRow(
            self.centered_label('Python path'), self._path_list)
        self._widget.setLayout(self._layout)

    def apply_preferences(self):
        result = []
        settings_ = settings.instance()
        python_path = self._path_list.paths()

        if python_path != self._initial_python_path:
            settings_['Python/python_path'] = python_path
            result.append(
                (A_LIBRARY_RELOAD,
                 self._app_core.reload_node_library))
        return result


class MatlabSettingsWidget(PreferencesWidgetInterface):
    """Settings concerning MATLAB"""

    def __init__(self, parent=None):
        super(MatlabSettingsWidget, self).__init__(parent)
        self._path = 'MATLAB'

    def initialize(self, app_core, current_flow):
        super(MatlabSettingsWidget, self).initialize(app_core, current_flow)
        self._widget = QtGui.QWidget()
        settings_ = settings.instance()
        self._initial_matlab_path = settings_['MATLAB/matlab_path']
        self._initial_matlab_jvm = settings_['MATLAB/matlab_jvm']

        self._path_line = QtGui.QLineEdit()
        self._path_button = QtGui.QPushButton('...')
        self._jvm_checkbox = QtGui.QCheckBox()

        if len(self._initial_matlab_path):
            self._path_line.setText(self._initial_matlab_path)
        self._jvm_checkbox.setChecked(settings_['MATLAB/matlab_jvm'])

        self._layout = self.create_layout()
        path_widget = QtGui.QHBoxLayout()
        path_widget.addWidget(self._path_line)
        path_widget.addWidget(self._path_button)
        self._layout.addRow(
            self.centered_label('MATLAB path'), path_widget)
        self._layout.addRow('Disable JVM', self._jvm_checkbox)
        self._widget.setLayout(self._layout)

        self._path_button.clicked.connect(self._get_path)

    def _get_path(self):
        default_directory = self._path_line.text()
        path = QtGui.QFileDialog.getOpenFileName(
            self._widget, 'Select MATLAB executable', default_directory)[0]
        if len(path):
            self._path_line.setText(path)

    def apply_preferences(self):
        result = []
        settings_ = settings.instance()
        matlab_path = self._path_line.text()
        jvm = self._jvm_checkbox.isChecked()
        value_changed = False

        if matlab_path != self._initial_matlab_path:
            settings_['MATLAB/matlab_path'] = matlab_path
            value_changed = True
        if jvm != self._initial_matlab_jvm:
            settings_['MATLAB/matlab_jvm'] = jvm
            value_changed = True
        if value_changed:
            result.append(
                (A_LIBRARY_RELOAD,
                 self._app_core.reload_node_library))
        return result


class ModifyEnvironmentWidget(QtGui.QWidget):
    valueChanged = QtCore.Signal()
    DEFAULT_FLOW_VARIABLES = [
        'SY_FLOW_FILEPATH', 'SY_FLOW_DIR', 'SY_PARENT_FLOW_FILEPATH']

    def __init__(self, parent=None):
        super(ModifyEnvironmentWidget, self).__init__(parent)
        self._init_gui()

    def _init_gui(self):
        self._hlayout = QtGui.QHBoxLayout()
        self._hlayout.setContentsMargins(0, 0, 0, 0)

        self._tablewidget = QtGui.QTableWidget()
        self._tablewidget.setColumnCount(2)
        self._tablewidget.setHorizontalHeaderLabels(['Name', 'Value'])

        self._vlayout = QtGui.QVBoxLayout()
        self._vlayout.setContentsMargins(0, 0, 0, 0)
        self._vlayout.setSpacing(5)

        self._name_lineedit = QtGui.QLineEdit()
        self._name_lineedit.setPlaceholderText('Name')
        self._value_lineedit = QtGui.QLineEdit()
        self._value_lineedit.setPlaceholderText('Value')
        self._add_button = QtGui.QPushButton('Add')
        self._remove_button = QtGui.QPushButton('Remove')

        self._hlayout.addWidget(self._name_lineedit)
        self._hlayout.addWidget(self._value_lineedit)
        self._hlayout.addWidget(self._add_button)

        self._vlayout.addLayout(self._hlayout)
        self._vlayout.addWidget(self._tablewidget)
        self._vlayout.addWidget(self._remove_button)

        self.setLayout(self._vlayout)

        self._add_button.clicked.connect(self._add_env_var)
        self._remove_button.clicked.connect(self._remove_env_var)

        self._tablewidget.itemChanged.connect(
            lambda: self.valueChanged.emit())

    def set_variables(self, variables):
        for name, value in variables.items():
            self._add(name, value)

    def variables(self):
        tw = self._tablewidget
        return {tw.item(row, 0).text(): tw.item(row, 1).text()
                for row in range(tw.rowCount())}

    def _add_env_var(self):
        name = self._name_lineedit.text()
        value = self._value_lineedit.text()
        self._add(name, value)

    def _add(self, name, value):
        row_count = self._tablewidget.rowCount()
        self._tablewidget.setRowCount(row_count + 1)

        self._tablewidget.blockSignals(True)

        name_item = QtGui.QTableWidgetItem(name)
        value_item = QtGui.QTableWidgetItem(value)
        self._tablewidget.setItem(row_count, 0, name_item)
        self._tablewidget.setItem(row_count, 1, value_item)
        if name in self.DEFAULT_FLOW_VARIABLES:
            name_item.setFlags(QtCore.Qt.NoItemFlags)
            value_item.setFlags(QtCore.Qt.NoItemFlags)

        self._tablewidget.resizeColumnsToContents()
        self._tablewidget.sortItems(0)
        self._tablewidget.blockSignals(False)

        self._tablewidget.setVerticalHeaderLabels(
            [six.text_type(i)
             for i in range(self._tablewidget.rowCount())])

        self.valueChanged.emit()

    def _remove_env_var(self):
        row = self._tablewidget.currentRow()
        remove = (
            row != -1 and
            self._tablewidget.item(row, 0).flags() != QtCore.Qt.NoItemFlags)
        if remove:
            self._tablewidget.removeRow(row)

        self.valueChanged.emit()

    def resize_to_content(self):
        self._tablewidget.resizeColumnsToContents()


class EnvironmentSettingsWidget(PreferencesWidgetInterface):
    """Settings concerning environment variables."""

    def __init__(self, parent=None):
        super(EnvironmentSettingsWidget, self).__init__(parent)
        self._path = 'Environment'

    def initialize(self, app_core, current_flow):
        super(EnvironmentSettingsWidget, self).initialize(app_core,
                                                          current_flow)
        self._widget = QtGui.QWidget()
        settings_ = settings.instance()
        self._layout = self.create_layout()
        self._init(settings_)

    def _init(self, settings_):
        self._global_env_widget = ModifyEnvironmentWidget()
        self._layout = self.create_layout()
        settings_ = settings.instance()
        env_vars = settings_['environment']

        self._global_env_widget.set_variables(
            dict([env_var.split('=', 1) for env_var in env_vars]))
        self._global_env_widget.setMaximumHeight(300)

        self._textedit = QtGui.QTextEdit()
        self._tablewidget = QtGui.QTableWidget()
        self._tablewidget.setColumnCount(2)
        self._tablewidget.setHorizontalHeaderLabels(['Name', 'Value'])

        self._update_table(ENV.prioritized_variables())

        vlayout = QtGui.QGridLayout()
        vlayout.addWidget(QtGui.QLabel('Global environment'), 0, 0)
        vlayout.addWidget(self._global_env_widget, 0, 1)
        vlayout.addWidget(QtGui.QLabel('Environment variables'), 1, 0)
        vlayout.addWidget(self._tablewidget, 1, 1)
        self._widget.setLayout(vlayout)

        self._global_env_widget.valueChanged.connect(self._update_globals)
        self._tablewidget.resizeColumnsToContents()
        self._global_env_widget.resize_to_content()

    def apply_preferences(self):
        result = []
        settings_ = settings.instance()
        global_env_vars = self._global_env_widget.variables()
        values = []
        for name, value in global_env_vars.items():
            values.append('{}={}'.format(name, value))
        ENV.set_global_variables(global_env_vars)
        settings_['environment'] = values
        return result

    @QtCore.Slot(dict)
    def _update_table(self, env_variables):
        self._tablewidget.setRowCount(len(env_variables))

        for row, (name, value) in enumerate(env_variables.items()):
            name_item = QtGui.QTableWidgetItem(name)
            value_item = QtGui.QTableWidgetItem(value)
            name_item.setFlags(QtCore.Qt.NoItemFlags)
            value_item.setFlags(QtCore.Qt.NoItemFlags)
            self._tablewidget.setItem(row, 0, name_item)
            self._tablewidget.setItem(row, 1, value_item)
        self._tablewidget.sortItems(0)

    @QtCore.Slot()
    def _update_globals(self):
        global_env_vars = self._global_env_widget.variables()
        prio_env_var = copy.deepcopy(
            ENV.prioritized_variables(exclude=('global',)))

        global_env_vars.update(prio_env_var)
        self._update_table(global_env_vars)
        self._global_env_widget.resize_to_content()
        self._tablewidget.resizeColumnsToContents()


class DebugSettingsWidget(PreferencesWidgetInterface):
    """Settings concerning debugging and profiling."""

    profile_path_types = ['Session folder', 'Workflow folder']

    def __init__(self, parent=None):
        super(DebugSettingsWidget, self).__init__(parent)
        self._path = 'Debug'

    def initialize(self, unused0, unused1):
        self._dot_in_path = distutils.spawn.find_executable(vs.str_('dot'))

        def graphviz_path_dialog():
            default_directory = self._graphviz_path.text()
            dir_ = QtGui.QFileDialog.getExistingDirectory(
                self._widget, 'Locate Graphviz directory containing dot',
                default_directory)
            if dir_:
                self._graphviz_path.setText(dir_)
                test_graphviz_path()

        def test_graphviz_path():
            gviz_path = self._graphviz_path.text()
            dot = distutils.spawn.find_executable(vs.str_('dot'), gviz_path)
            if dot:
                self._graphviz_status.setText("Graphviz found!")
                self._graphviz_status.setStyleSheet("QLabel { color: green; }")
            elif self._dot_in_path:
                self._graphviz_status.setText("Graphviz found in PATH!")
                self._graphviz_status.setStyleSheet("QLabel { color: green; }")
            else:
                self._graphviz_status.setText("Graphviz not found!")
                self._graphviz_status.setStyleSheet("QLabel { color: red; }")

        super(DebugSettingsWidget, self).initialize(unused0, unused1)
        self._widget = QtGui.QWidget()
        settings_ = settings.instance()
        path_type = settings_['Debug/profile_path_type']
        graphviz_path = settings_['Debug/graphviz_path']

        self._profile_path_type = QtGui.QComboBox()
        self._profile_path_type.addItems(self.profile_path_types)
        self._profile_path_type.setCurrentIndex(
            self._profile_path_type.findText(path_type))

        gviz_path_layout = QtGui.QHBoxLayout()
        self._graphviz_path = QtGui.QLineEdit(graphviz_path)
        file_button = QtGui.QPushButton('...')
        gviz_path_layout.addWidget(self._graphviz_path)
        gviz_path_layout.addWidget(file_button)

        self._graphviz_status = QtGui.QLabel()

        self._layout = self.create_layout()
        self._layout.addRow('Store profiling data in', self._profile_path_type)
        self._layout.addRow(
            self.centered_label('Graphviz install path'),
            gviz_path_layout)
        self._layout.addRow('', self._graphviz_status)
        self._widget.setLayout(self._layout)

        self._graphviz_path.textEdited.connect(test_graphviz_path)
        file_button.clicked.connect(graphviz_path_dialog)

        test_graphviz_path()

    def apply_preferences(self):
        settings_ = settings.instance()
        settings_[
            'Debug/profile_path_type'] = self._profile_path_type.currentText()
        settings_['Debug/graphviz_path'] = self._graphviz_path.text()


class TempFilesSettingsWidget(PreferencesWidgetInterface):
    """Temporary files settings"""

    def __init__(self, parent=None):
        super(TempFilesSettingsWidget, self).__init__(parent)
        self._path = 'Temporary files'
        self._apply_order = 10000

    def initialize(self, app_core, current_flow):
        super(TempFilesSettingsWidget, self).initialize(app_core, current_flow)
        self._widget = QtGui.QWidget()
        settings_ = settings.instance()
        self._layout = self.create_layout()
        self._init_temp_path(settings_)

    def _init_temp_path(self, settings_):
        self._path_layout = QtGui.QHBoxLayout()
        temp_path = settings_['temp_folder']
        self._original_temp_path = temp_path
        self._temp_path = QtGui.QLineEdit(temp_path)
        self._path_layout.addWidget(self._temp_path)

        self._file_button = QtGui.QPushButton('...')
        self._file_button.clicked.connect(self._open_temp_path_dialog)
        self._path_layout.addWidget(self._file_button)
        self._layout.addRow(
            self.centered_label('Temporary files path'),
            self._path_layout)

        self._remove_temp_files = QtGui.QCheckBox()
        if settings_['remove_temp_files']:
            self._remove_temp_files.setChecked(True)
        self._layout.addRow(
            'Remove temporary files on close', self._remove_temp_files)

        self._temp_age = QtGui.QSpinBox()
        self._temp_age.setMaximum(999999)
        self._temp_age.setValue(settings_['max_temp_folder_age'])
        self._layout.addRow(
            'Maximum age of temporary files (days)', self._temp_age)

        self._temp_size = QtGui.QLineEdit()
        self._temp_size.setText(settings_['max_temp_folder_size'])
        self._temp_size.setSizePolicy(
            QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self._temp_size.setMaximumSize(QtCore.QSize(70, 25))
        self._layout.addRow(
            'Maximum size of temporary files (x k/M/G)', self._temp_size)

        self._temp_number = QtGui.QSpinBox()
        self._temp_number.setMaximum(999999)
        self._temp_number.setValue(settings_['max_temp_folder_number'])
        self._layout.addRow(
            'Maximum number of temporary file session folders',
            self._temp_number)
        self._widget.setLayout(self._layout)

    @QtCore.Slot()
    def _open_temp_path_dialog(self):
        default_directory = self._temp_path.text()
        dir_ = QtGui.QFileDialog.getExistingDirectory(
            self._widget, 'Locate a directory for temporary files',
            default_directory)
        if len(dir_) > 0:
            self._temp_path.setText(dir_)

    def apply_preferences(self):
        settings_ = settings.instance()

        if self._original_temp_path != self._temp_path.text():
            settings_['temp_folder'] = six.text_type(self._temp_path.text())
        else:
            settings_['temp_folder'] = self._temp_path.text()

        settings_['remove_temp_files'] = self._remove_temp_files.isChecked()
        settings_['max_temp_folder_age'] = int(self._temp_age.text())
        settings_['max_temp_folder_number'] = self._temp_number.value()


class AdvancedSettingsWidget(PreferencesWidgetInterface):
    """Advanced settings"""

    def __init__(self, parent=None):
        super(AdvancedSettingsWidget, self).__init__(parent)
        self._path = 'Advanced'
        self._apply_order = 10000

    def initialize(self, app_core, current_flow):
        super(AdvancedSettingsWidget, self).initialize(app_core, current_flow)
        self._widget = QtGui.QWidget()
        self._layout = self.create_layout()
        self._init_advanced(settings.instance())

    def _init_advanced(self, settings_):
        self._nbr_of_threads = QtGui.QSpinBox()
        self._nbr_of_threads.setMaximum(999)
        self._nbr_of_threads.setValue(settings_['max_nbr_of_threads'])

        self._char_limit = QtGui.QSpinBox()
        self._char_limit.setMaximum(2**31 - 1)  # Max 32 bit signed int.
        self._char_limit.setValue(settings_['max_task_chars'])

        self._deprecated_warning = QtGui.QCheckBox()
        self._deprecated_warning.setChecked(settings_['deprecated_warning'])

        self._clear_settings = QtGui.QCheckBox()
        self._clear_settings.setChecked(settings_.get('clear_settings', False))
        self._clear_caches = QtGui.QCheckBox()
        self._clear_caches.setChecked(settings_.get('clear_caches', False))

        self._show_experimental = QtGui.QCheckBox()
        self._show_experimental.setChecked(settings_['Gui/experimental'])

        clear_layout = QtGui.QGridLayout()
        clear_layout.addWidget(QtGui.QLabel('Caches'), 0, 0)
        clear_layout.addWidget(self._clear_caches, 1, 0,
                               QtCore.Qt.AlignHCenter)
        clear_layout.addWidget(QtGui.QLabel('Settings'), 0, 1)
        clear_layout.addWidget(
            self._clear_settings, 1, 1, QtCore.Qt.AlignHCenter)
        clear_layout.setHorizontalSpacing(10)
        clear_layout.setVerticalSpacing(2)

        self._layout.addRow(
            'Maximum number of concurrent node threads.\n'
            '0 = automatic\n'
            'Sympathy has to be restarted to apply this setting.',
            self._nbr_of_threads)

        self._layout.addRow(
            'Character limit\n'
            '0 = unlimited',
            self._char_limit)

        self._layout.addRow(
            'Display warnings for deprecated nodes.',
            self._deprecated_warning)
        self._layout.addRow(
            'Reset on next close:\n'
            'CAUTION! This may affect all open instances of Sympathy.',
            clear_layout)
        self._layout.addRow('Show experimental options\n'
                            'Preferences has to be reopened before this '
                            'takes effect.',
                            self._show_experimental)

        self._widget.setLayout(self._layout)

    def apply_preferences(self):
        settings_ = settings.instance()
        settings_['max_nbr_of_threads'] = self._nbr_of_threads.value()
        settings_['deprecated_warning'] = self._deprecated_warning.isChecked()
        settings_['clear_settings'] = self._clear_settings.isChecked()
        settings_['clear_caches'] = self._clear_caches.isChecked()
        settings_['max_task_chars'] = self._char_limit.value()
        settings_['Gui/experimental'] = self._show_experimental.isChecked()


class LibraryViewWidget(PreferencesWidgetInterface):
    """Library view settings"""

    library_type_changed = QtCore.Signal(six.text_type)
    library_type_disk_hide_changed = QtCore.Signal()
    library_highlighter_changed = QtCore.Signal(tuple)

    def __init__(self, parent=None):
        super(LibraryViewWidget, self).__init__(parent)
        self._path = 'Library View'

    def initialize(self, app_core, current_flow):
        super(LibraryViewWidget, self).initialize(app_core, current_flow)
        self._widget = QtGui.QWidget()
        settings_ = settings.instance()

        self._layout = self.create_layout()
        self._init_gui_settings(settings_)

    def _init_gui_settings(self, settings_):
        self._library_type = QtGui.QComboBox()
        choices = [
            'FlatTag layout', 'Tag layout',
            'Separated Tag layout', 'Disk layout']
        self._library_type.addItems(choices)
        self._library_type.setCurrentIndex(choices.index(
            settings_['Gui/library_type']))

        self._hide_hidden = QtGui.QCheckBox()
        self._hide_hidden.setChecked(settings_['Gui/library_hide'])

        layout_sublayout = QtGui.QHBoxLayout()
        layout_sublayout.addWidget(self._library_type)
        layout_sublayout.addWidget(
            QtGui.QLabel('Hide deprecated nodes in Disk layout'))
        layout_sublayout.addWidget(self._hide_hidden)
        layout_sublayout.setSpacing(5)

        self._library_matcher_type = QtGui.QComboBox()
        choices = ['character', 'word']
        self._library_matcher_type.addItems(choices)
        self._library_matcher_type.setCurrentIndex(choices.index(
            settings_['Gui/library_matcher_type']))

        self._library_highlighter_type = QtGui.QComboBox()
        choices = ['color', 'background-color', 'font-weight']
        self._library_highlighter_type.addItems(choices)
        self._library_highlighter_type.setCurrentIndex(choices.index(
            settings_['Gui/library_highlighter_type']))

        self._library_highlighter_color = QtGui.QLineEdit()
        self._library_highlighter_color.setText(
            settings_['Gui/library_highlighter_color'].upper())
        self._library_highlighter_color.setFixedWidth(100)

        self._color_button = QtGui.QPushButton('...')
        self._color_button.clicked.connect(self._set_color)

        color_layout = QtGui.QHBoxLayout()
        color_layout.addWidget(self._library_highlighter_color)
        color_layout.addWidget(self._color_button)
        self._color_button.setFixedWidth(55)

        self._quickview_popup_position = QtGui.QComboBox()
        choices = ['left', 'center', 'right']
        self._quickview_popup_position.addItems(choices)
        self._quickview_popup_position.setCurrentIndex(choices.index(
            settings_['Gui/quickview_popup_position']))

        self._layout.addRow('Type', layout_sublayout)
        self._layout.addRow('Highlighter', self._library_matcher_type)
        self._layout.addRow('Highlighter type', self._library_highlighter_type)
        self._layout.addRow('Highlighter color', color_layout)
        self._layout.addRow('Popup position', self._quickview_popup_position)

        self._widget.setLayout(self._layout)

        self._library_highlighter_type.currentIndexChanged.connect(
            self._disable_colorfield)
        self._library_type.currentIndexChanged.connect(self._enable_hide)
        self._enable_hide()
        self._disable_colorfield()

    def _disable_colorfield(self):
        if self._library_highlighter_type.currentText() == 'font-weight':
            self._library_highlighter_color.setDisabled(True)
            self._color_button.setDisabled(True)
        else:
            self._library_highlighter_color.setDisabled(False)
            self._color_button.setDisabled(False)

    def _enable_hide(self):
        if self._library_type.currentText() == 'Disk layout':
            self._hide_hidden.setEnabled(True)
        else:
            self._hide_hidden.setEnabled(False)

    def _set_color(self):
        picker = QtGui.QColorDialog()
        res = picker.exec_()
        if res == QtGui.QDialog.Accepted:
            self._library_highlighter_color.setText(
                picker.currentColor().name().upper())

    def apply_preferences(self):
        result = []
        settings_ = settings.instance()

        library_type = self._library_type.currentText()
        library_type_prev = settings_['Gui/library_type']
        settings_['Gui/library_type'] = library_type
        if library_type_prev != library_type:
            result.append(
                (A_LIBRARY_TYPE,
                 lambda:
                 self.library_type_changed.emit(library_type.split(' ')[0])))
        hide_hidden = self._hide_hidden.isChecked()
        hide_hidden_prev = settings_['Gui/library_hide']
        settings_['Gui/library_hide'] = hide_hidden
        if hide_hidden_prev != hide_hidden:
            result.append(
                (A_LIBRARY_TYPE,
                 lambda: self.library_type_disk_hide_changed.emit()))

        lib_highlighter_type = self._library_highlighter_type.currentText()
        lib_highlighter_type_prev = settings_['Gui/library_highlighter_type']
        settings_['Gui/library_highlighter_type'] = lib_highlighter_type

        lib_highlighter_color = self._library_highlighter_color.text()
        lib_highlighter_color_prev = settings_[
            'Gui/library_highlighter_color']
        settings_['Gui/library_highlighter_color'] = lib_highlighter_color

        lib_matcher_type = self._library_matcher_type.currentText()
        lib_matcher_type_prev = settings_['Gui/library_matcher_type']
        settings_['Gui/library_matcher_type'] = lib_matcher_type

        if (lib_highlighter_type_prev != lib_highlighter_type or
                lib_highlighter_color_prev != lib_highlighter_color or
                lib_matcher_type_prev != lib_matcher_type):
            result.append(
                (A_LIBRARY_HIGHLIGHTER,
                 lambda: self.library_highlighter_changed.emit((
                     lib_matcher_type,
                     lib_highlighter_type,
                     lib_highlighter_color
                 ))))

        quickview_popup_pos = self._quickview_popup_position.currentText()
        settings_['Gui/quickview_popup_position'] = quickview_popup_pos

        return result
