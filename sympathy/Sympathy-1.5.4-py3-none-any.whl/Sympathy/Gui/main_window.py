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
"""Main window (menu bar, dock widgets)"""
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import logging
import sys
import os
import subprocess
import functools

import six
import PySide.QtCore as QtCore
import PySide.QtGui as QtGui

from . import flow
from . import flow_window
from . import messages_window
from . import control_panel
from . import flow_overview
from . import about_window
from . import library_view
from . import preferences
from . import settings
from . import util
from . import signals
from . import nodewizard
from . import functionwizard
from . import librarywizard
from . import common
from Gui.environment_variables import instance as env_instance
from sympathy.utils.prim import nativepath
from sympathy.platform import os_support, exceptions


# Dropping files from OS X 10.10 can result in mimedata containing file ids on
# the form "file:///.file/id=xxxxxxx.xxxxxx". Qt4 doesn't convert these
# automatically so we need to do it ourselves. See Qt bug:
# https://bugreports.qt.io/browse/QTBUG-40449 for more information.
if sys.platform == 'darwin':
    # Only OS X will produce file ids.
    try:
        from Cocoa import NSURL, NSString
        from Foundation import NSBundle
        _has_cocoa = True
    except ImportError:
        # If cocoa is not available, we can't do anything. Dropping files into
        # Sympathy might not work in this case.
        _has_cocoa = False
else:
    _has_cocoa = False

if _has_cocoa:
    # Replace 'Python' with 'Sympathy for Data' in the Mac OS menu
    bundle = NSBundle.mainBundle()
    if bundle:
        info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
        if (info is not None and ('CFBundleName' not in info or
                                  info['CFBundleName'] == 'Python')):
            # The info dictionary is empty for some reason on macOS 10.13,
            # and perhaps lower versions, so add CFBundleName if missing.
            # For macOS 10.10 the dictionary is populated.
            info['CFBundleName'] = 'Sympathy for Data'

    def file_ids_to_paths(urls):
        """Translate file ids to paths."""
        new_urls = []
        for url in urls:
            ns_string = NSString.stringWithUTF8String_(
                url.path().encode('utf8'))
            ns_url = NSURL.fileURLWithPath_(ns_string)
            if ns_url.isFileReferenceURL():
                # Only translate if the url is a reference e.g.,
                # file:///.file/id=xxxxxxx.xxxxxx
                new_urls.append(QtCore.QUrl(str(ns_url.filePathURL())))
            else:
                # Return the original url if it is a path.
                new_urls.append(url)
        return new_urls
else:
    def file_ids_to_paths(urls):
        return urls


core_logger = logging.getLogger('core')


def icon_path(icon):
    """Return icon path for icon"""
    return os.path.join(util.icon_path('actions'), icon)


class FlowTabWidget(QtGui.QTabWidget):
    """Keeper of flow tabs."""

    flow_deleted = QtCore.Signal(flow.Flow)
    current_flow_changed = QtCore.Signal(flow_window.FlowWindow)

    def __init__(self, parent=None):
        super(FlowTabWidget, self).__init__(parent)
        self._signals = signals.SignalHandler()
        self.tabBar().tabCloseRequested[int].connect(self.close_tab)
        self.tabBar().currentChanged[int].connect(self.change_tab)
        self.setMovable(True)
        self.setTabsClosable(True)
        self._flow_windows = {}

    def get_flows(self):
        return [self.widget(index).flow() for index in range(self.count())]

    def get_current_flow(self):
        current_widget = self.currentWidget()
        if not current_widget:
            return None
        else:
            return current_widget.flow()

    def close_flow_tab(self, flow_):
        """Close tab with given flow"""
        self._signals.disconnect_all(flow_)
        flow_window_ = self._flow_windows.get(flow_)
        del self._flow_windows[flow_]
        if flow_window_:
            index = self.indexOf(flow_window_)
            flow_window_.close_flow_view()
            self.removeTab(index)
        self.update_flow_labels()

    def open_flow_window_tab(self, flow_window_):
        """Add a new tab"""
        flow_ = flow_window_.flow()
        self._flow_windows[flow_] = flow_window_
        self.addTab(flow_window_, '')
        self.update_flow_labels()
        self._signals.connect_reference(flow_, [
            (flow_.clean_changed, self.update_flow_labels),
            (flow_.subflow_clean_changed, self.update_flow_labels)])

    def get_scratch_flow(self):
        """
        If the only open flow is unchanged and unsaved return it, else return
        None. The returned flow (if any) can safely be closed.
        """
        if self.count() == 1:
            flow_ = self.widget(0).flow()
            if not flow_.filename and not flow_.undo_stack().count():
                return flow_
        return None

    @QtCore.Slot(int)
    def close_tab(self, tab_index):
        """Close tab with index"""
        flow_window_ = self.widget(tab_index)
        return flow_window_.close_flow()

    @QtCore.Slot(int)
    def change_tab(self, index):
        """Bring tab #index to front"""
        self.current_flow_changed.emit(self.widget(index))

    def show_flow(self, flow_):
        """Bring tab with flow to front"""
        flow_window_ = self._flow_windows.get(flow_)
        if flow_window_:
            index = self.indexOf(flow_window_)
            self.setCurrentIndex(index)

    def update_flow_labels(self):
        """Update tab labels for all flows."""
        def get_destinguishing_parts(name_tuple, all_name_tuples):
            same_shortname_tuples = [
                t for t in all_name_tuples if t[-1] == name_tuple[-1]]
            same_shortname_tuples.remove(name_tuple)  # Remove the current flow

            distinguishing_parts = []
            for pos, part in enumerate(name_tuple):
                other_parts = []
                for same_shortname_tuple in same_shortname_tuples:
                    try:
                        other_parts.append(same_shortname_tuple[pos])
                    except IndexError:
                        # Can happen if same_shortname_tuple is shorter than
                        # name_tuple.
                        other_parts.append(None)

                same_parts = [other_part == part for other_part in other_parts]
                if not all(same_parts):
                    # Since this part differs for some of the flows, it can be
                    # used to distinguish between them.
                    distinguishing_parts.append(part)

                    # Any subflows that differ for this part have now been
                    # distinguished, so we can remove them from further
                    # consideration.
                    same_shortname_tuples = [
                        t for i, t in enumerate(same_shortname_tuples)
                        if same_parts[i]]
            return distinguishing_parts

        flows = [self.widget(i).flow() for i in range(self.count())]
        flow_name_tuples = [f.full_display_name_tuple for f in flows]

        for name_tuple, flow_ in zip(flow_name_tuples, flows):
            distinguishing_parts = get_destinguishing_parts(
                name_tuple, flow_name_tuples)
            flow_dirty = not flow_.is_clean()
            subflows_dirty = (
                flow_.is_root_flow() and not flow_.subflows_are_clean())

            # Tab label
            label = name_tuple[-1]
            if distinguishing_parts:
                label += " <{}>".format("/".join(distinguishing_parts))
            if flow_dirty or subflows_dirty:
                label += "*"
            flow_window = self._flow_windows[flow_]
            tab_index = self.indexOf(flow_window)
            self.setTabText(tab_index, label)

            # Tab tooltip
            tooltip_parts = [" -> ".join(name_tuple), ""]
            filename = flow_.root_or_linked_flow_filename
            if filename:
                tooltip_parts.append("Saved in {}".format(filename))
            else:
                tooltip_parts.append("Not yet saved")
            if flow_dirty:
                tooltip_parts.append("There are unsaved changes in this flow.")
            elif subflows_dirty:
                tooltip_parts.append("There are unsaved changes in some "
                                     "linked subflows.")
            self.setTabToolTip(tab_index, "\n".join(tooltip_parts))

    def preferences_updated(self):
        for flow_window_ in self._flow_windows.values():
            flow_window_.preferences_updated()


class MenuManager(QtCore.QObject):
    """Manages the main menu bar."""

    new_flow = QtCore.Signal()
    new_node = QtCore.Signal()
    new_function = QtCore.Signal()
    new_library = QtCore.Signal()
    open_flow = QtCore.Signal()
    open_named_flow = QtCore.Signal(six.text_type)
    reload_library = QtCore.Signal()
    open_preferences = QtCore.Signal()
    quit_application = QtCore.Signal()
    toggle_fullscreen = QtCore.Signal()
    find_nodes = QtCore.Signal()
    about_sympathy = QtCore.Signal()
    user_documentation = QtCore.Signal()
    node_library = QtCore.Signal()
    create_documentation = QtCore.Signal()

    def __init__(self, main_window, parent=None):
        super(MenuManager, self).__init__(parent)
        self._main_window = main_window
        self._control_panel = main_window._control_panel
        self._platform_is_mac = sys.platform == 'darwin'
        self._init()

    def _create_action(self, name, signal, icon=None, shortcut=None):
        action = QtGui.QAction(name, self)
        action.triggered.connect(signal)
        if icon:
            action.setIcon(QtGui.QIcon(icon))
        if shortcut:
            action.setShortcut(shortcut)
        return action

    def _init(self):
        self._menu_bar = None
        self._window_file_menu_actions = []
        self._window_edit_menu_actions = []
        self._window_control_menu_actions = []
        self._window_view_menu_actions = []
        self._window_view_extra_menu_actions = []

        self._new_flow = self._create_action(
            '&New Flow', self.new_flow, icon_path('document-new-symbolic.svg'),
            QtGui.QKeySequence.New)

        self._new_library = self._create_action(
            'New Library',
            self.new_library)
        self._new_library.setEnabled(True)

        self._new_node = self._create_action(
            'New Node',
            self.new_node)
        self._new_node.setEnabled(True)

        self._new_function = self._create_action(
            'New Function',
            self.new_function)
        self._new_function.setEnabled(True)

        self._open_flow = self._create_action(
            '&Open...',
            self.open_flow,
            icon_path('document-open-symbolic.svg'),
            QtGui.QKeySequence.Open)

        self._control_panel.new_signal.connect(self.new_flow)
        self._control_panel.open_signal.connect(self.open_flow)
        self._control_panel.set_current_flow(None)

        self._reload_library = self._create_action(
            'Reload &Library', self.reload_library, shortcut='Ctrl+Shift+R')

        self._preferences = self._create_action(
            '&Preferences', self.open_preferences,
            shortcut=QtGui.QKeySequence.Preferences)
        self._preferences.setMenuRole(QtGui.QAction.PreferencesRole)

        if self._platform_is_mac:
            quit_menu_item_text = 'Quit'
            about_menu_item_text = 'About'
        else:
            quit_menu_item_text = '&Quit'
            about_menu_item_text = '&About'
        self._quit = self._create_action(
            quit_menu_item_text, self.quit_application,
            icon_path('system-shutdown-symbolic'),
            QtGui.QKeySequence.Quit)
        self._quit.setMenuRole(QtGui.QAction.QuitRole)

        self._find_nodes = self._create_action(
            '&Find...',
            self.find_nodes,
            icon_path('edit-find-symbolic.svg'),
            QtGui.QKeySequence.Find)

        if self._platform_is_mac:
            # Use same shortcut as finder and safari
            fullscreen_keysequence = QtGui.QKeySequence("Ctrl+Shift+F")
        else:
            fullscreen_keysequence = QtGui.QKeySequence(QtCore.Qt.Key_F11)
        self._fullscreen = self._create_action(
            'Toggle &Fullscreen', self.toggle_fullscreen,
            icon_path('view-fullscreen-symbolic.svg'),
            fullscreen_keysequence)

        self._about = self._create_action(about_menu_item_text,
                                          self.about_sympathy)
        self._about.setMenuRole(QtGui.QAction.AboutRole)
        self._user_documentation = self._create_action('&User Manual',
                                                       self.user_documentation)
        self._node_library = self._create_action('Node &Libraries',
                                                 self.node_library)
        self._open_examples = self._create_action(
            'View Example Flows', self._open_example_folder)
        self._create_documentation = self._create_action(
            '&Create Documentation', self.create_documentation)

    def _open_example_folder(self):
        try:
            lib_dir = settings.instance()['Python/library_path'][0]
        except IndexError:
            exceptions.sywarn('No node libraries found!')
            return

        example_dir = os.path.join(lib_dir, 'Examples')
        if not os.path.isabs(example_dir):
            example_dir = os.path.normpath(
                os.path.join(os.environ['SY_APPLICATION_DIR'], example_dir))

        if os.path.isdir(example_dir):
            os_support.run_filename(example_dir)
        else:
            msg = (
                'The examples in "{}" seem to be missing.'.format(example_dir))
            if six.PY2:
                msg = msg.encode(sys.getfilesystemencoding())
            exceptions.sywarn(msg)

    def _add_actions_from_list(self, menu, action_list):
        for action in action_list:
            if action:
                menu.addAction(action)
            else:
                menu.addSeparator()

    def _update_file_menu(self):
        file_menu = self._menu_bar.addMenu('&File')
        file_menu.addAction(self._new_flow)
        file_menu.addAction(self._new_library)
        file_menu.addAction(self._new_node)
        file_menu.addAction(self._new_function)
        file_menu.addAction(self._open_flow)
        recent_flows_menu = file_menu.addMenu('Open &Recent')
        for (idx, flow_name) in enumerate(
                settings.instance()['Gui/recent_flows']):
            action = QtGui.QAction('&{}: {}'.format(idx + 1, flow_name), self)
            action.triggered.connect(
                functools.partial(self.open_named_flow.emit, flow_name))
            recent_flows_menu.addAction(action)
        file_menu.addSeparator()
        self._add_actions_from_list(file_menu, self._window_file_menu_actions)
        file_menu.addSeparator()
        file_menu.addAction(self._preferences)
        file_menu.addAction(self._reload_library)
        file_menu.addSeparator()
        file_menu.addAction(self._quit)
        self._menu_bar.addMenu(file_menu)

    def _update_edit_menu(self):
        if self._window_edit_menu_actions:
            edit_menu = self._menu_bar.addMenu('&Edit')
            self._add_actions_from_list(
                edit_menu, self._window_edit_menu_actions)
            edit_menu.addSeparator()
            edit_menu.addAction(self._find_nodes)
            self._menu_bar.addMenu(edit_menu)

    def _update_control_menu(self):
        if self._window_control_menu_actions:
            control_menu = self._menu_bar.addMenu('&Control')
            self._add_actions_from_list(
                control_menu, self._window_control_menu_actions)
            self._menu_bar.addMenu(control_menu)

    def _update_view_menu(self):
        view_menu = self._menu_bar.addMenu('&View')
        self._add_actions_from_list(
            view_menu, self._window_view_extra_menu_actions +
            self._window_view_menu_actions)
        self._menu_bar.addMenu(view_menu)
        view_menu.addSeparator()
        view_menu.addAction(self._fullscreen)

    def _update_help_menu(self):
        help_menu = self._menu_bar.addMenu('&Help')
        help_menu.addAction(self._user_documentation)
        help_menu.addAction(self._node_library)
        help_menu.addAction(self._open_examples)
        help_menu.addAction(self._create_documentation)
        help_menu.addSeparator()
        help_menu.addAction(self._about)
        self._menu_bar.addMenu(help_menu)

    def update_menus(self):
        self._menu_bar = self._main_window.menuBar()
        self._menu_bar.clear()
        self._update_file_menu()
        self._update_edit_menu()
        self._update_control_menu()
        self._update_view_menu()
        self._update_help_menu()

    def set_window_menus(self, flow_window_):
        self._window_file_menu_actions = []
        self._window_edit_menu_actions = []
        self._window_control_menu_actions = []
        self._window_view_menu_actions = []

        if flow_window_:
            self._window_file_menu_actions = (
                self._control_panel.file_menu_actions())

            self._window_edit_menu_actions = flow_window_.edit_menu_actions()
            self._window_edit_menu_actions.extend(
                self._control_panel.edit_menu_actions())

            self._window_control_menu_actions = (
                self._control_panel.control_menu_actions())

            self._window_view_menu_actions = flow_window_.view_menu_actions()
            self._window_view_menu_actions.extend(
                self._control_panel.view_menu_actions())

        self._control_panel.set_current_flow(flow_window_)

        self.update_menus()

    def set_window_view_extra_menu_actions(self, view_menu_actions):
        self._window_view_extra_menu_actions = view_menu_actions
        self.update_menus()


class MainWindow(QtGui.QMainWindow):
    """Main window."""

    new_flow = QtCore.Signal()
    open_flow = QtCore.Signal(six.text_type)
    open_named_flow = QtCore.Signal(six.text_type)
    open_flow_window = QtCore.Signal(flow.Flow)

    def __init__(self, app_core, args, parent=None):
        super(MainWindow, self).__init__(parent)
        self._app_core = app_core
        self._args = args
        self._wd = six.moves.getcwd()
        self._init()
        self._init_flow_overview()
        self._init_error_view()
        app_core.reload_node_library()
        if args.generate_documentation:
            app_core.reload_documentation()
        self._init_library_view()
        self._init_menu_manager()
        library_toggle_action = self._library_dock.toggleViewAction()
        library_toggle_action.setText("&Library")
        error_toggle_action = self._error_dock.toggleViewAction()
        error_toggle_action.setText("&Messages")
        flow_overview_toggle_action = (
            self._flow_overview_dock.toggleViewAction())
        flow_overview_toggle_action.setText("&Flow overview")
        self._menu_manager.set_window_view_extra_menu_actions(
            [library_toggle_action, flow_overview_toggle_action,
             error_toggle_action])
        self._docs_builder_view = None
        self._has_quit = False
        self._set_docking_state()

        settings_ = settings.instance()
        if 'Gui/geometry' in settings_:
            self.restoreGeometry(settings_['Gui/geometry'])
        if 'Gui/window_state' in settings_:
            self.restoreState(settings_['Gui/window_state'])
        if 'environment' in settings_:
            env = env_instance()
            env_vars = settings_['environment']
            for env_var in env_vars:
                name, value = env_var.split('=', 1)
                env.set_global_variable(name, value)

    def _init(self):
        self.setWindowTitle('Sympathy for Data')
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self._control_panel = control_panel.ControlPanel(self)
        self._control_panel.setObjectName('Gui::MainWindow::ControlPanel')
        self.addToolBar(QtCore.Qt.TopToolBarArea, self._control_panel)
        self._tab_widget = FlowTabWidget(parent=self)
        self._tab_widget.current_flow_changed.connect(
            self.current_flow_changed)

        self.setCentralWidget(self._tab_widget)
        self.setAcceptDrops(True)
        self.setGeometry(QtCore.QRect(10, 10, 800, 600))
        general_settings_widget = preferences.GeneralSettingsWidget(
            self._app_core)

        library_view_widget = preferences.LibraryViewWidget(self._app_core)
        self._library_type_changed = library_view_widget.library_type_changed
        self._library_type_disk_hide_changed = (
            library_view_widget.library_type_disk_hide_changed)
        self._library_highlighter_changed = (
            library_view_widget.library_highlighter_changed)

        libraries_settings_widget = preferences.LibrariesSettingsWidget(
            self._app_core)

        self._preference_widgets = [
            general_settings_widget,
            library_view_widget,
            libraries_settings_widget,
            preferences.PythonSettingsWidget(self._app_core),
            preferences.MatlabSettingsWidget(self._app_core),
            preferences.EnvironmentSettingsWidget(self._app_core),
            preferences.DebugSettingsWidget(None),
            preferences.TempFilesSettingsWidget(None),
            preferences.AdvancedSettingsWidget(None)]

        libraries_settings_widget.library_path_changed.connect(
            self._global_library_path_changed)

    def _init_menu_manager(self):
        def toggle_fullscreen():
            if self.windowState() & QtCore.Qt.WindowFullScreen:
                self.showNormal()
            else:
                self.showFullScreen()

        self._menu_manager = MenuManager(self, parent=self)
        self._menu_manager.update_menus()
        self._menu_manager.new_flow.connect(self.new_flow)
        self._menu_manager.new_node.connect(self._show_nodewizard)
        self._menu_manager.new_function.connect(self._show_functionwizard)
        self._menu_manager.new_library.connect(self._show_librarywizard)
        self._menu_manager.open_flow.connect(self._handle_open_flow)
        self._menu_manager.open_named_flow.connect(self.open_named_flow)
        self._menu_manager.reload_library.connect(self.reload_library)
        self._menu_manager.open_preferences.connect(self.show_preferences)
        self._menu_manager.quit_application.connect(self.quit_application)
        self._menu_manager.about_sympathy.connect(self._show_about_sympathy)
        self._menu_manager.find_nodes.connect(self._find_nodes)
        self._menu_manager.toggle_fullscreen.connect(toggle_fullscreen)
        self._menu_manager.user_documentation.connect(
            functools.partial(self.open_documentation, 'index'))
        self._menu_manager.node_library.connect(
            functools.partial(self.open_documentation, 'node_library'))
        self._menu_manager.create_documentation.connect(self._build_docs)

    def _find_nodes(self):
        self._flow_overview_dock.show()
        self._flow_overview.focus_search()

    def _global_library_path_changed(self):
        current_flow = self._tab_widget.get_current_flow()
        self._library_view.update_libraries(flow=current_flow)

    @QtCore.Slot()
    def _handle_open_flow(self):
        current_flow = self._tab_widget.get_current_flow()
        default_directory = ''
        if current_flow is not None:
            flow_filename = current_flow.root_or_linked_flow_filename
            if flow_filename:
                default_directory = os.path.dirname(flow_filename)
        self.open_flow.emit(default_directory)

    def _init_library_view(self):
        self._library_dock = QtGui.QDockWidget('Library', parent=self)
        self._library_dock.setObjectName('Gui::MainWindow::Library')
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self._library_dock)
        self._library_view = library_view.LibraryView(
            parent=self._library_dock)

        settings_ = settings.instance()
        model_type = settings_['Gui/library_type'].split(' ')[0]
        matcher_type = settings_['Gui/library_matcher_type']
        highlighter_type = settings_['Gui/library_highlighter_type']
        highlighter_color = settings_['Gui/library_highlighter_color']

        self._library_view.set_highlighter(
            (matcher_type, highlighter_type, highlighter_color))

        library_item_model = library_view.FlatTagLibraryModel(
            self._app_core.library_root(), self.style(),
            model_type=model_type,
            parent=self._library_dock)
        self._app_core.node_library_added.connect(
            self._library_view.update_model)

        self._app_core.flow_libraries_changed.connect(
            self._library_view.update_libraries)

        self._library_view.set_model(library_item_model)
        self._library_type_changed.connect(self._library_view.set_model_type)
        self._library_type_disk_hide_changed.connect(
            self._library_view.update_model)
        self._library_highlighter_changed.connect(
            self._library_view.set_highlighter)
        self._library_dock.setWidget(self._library_view)

    def _init_error_view(self):
        self._error_dock = QtGui.QDockWidget('Messages', parent=self)
        self._error_dock.setObjectName('Gui::MainWindow::Error')
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self._error_dock)
        self._error_view = messages_window.ErrorWidget(
            self._app_core, parent=self._error_dock)
        self._error_view.goto_node_requested.connect(self._handle_zoom_to_node)

        self._error_dock.setWidget(self._error_view)
        self._app_core.node_error_message[
            six.text_type, six.text_type].connect(
                self._error_view.add_message)
        self._app_core.node_output_received[six.text_type, dict].connect(
            self._error_view.add_node_output_message)
        self._app_core.node_library_output.connect(
            self._error_view.add_node_output_message)

    def _init_flow_overview(self):
        self._flow_overview_dock = QtGui.QDockWidget(
            'Flow overview', parent=self)
        self._flow_overview_dock.hide()
        self._flow_overview_dock.setObjectName('Gui::MainWindow::FlowOverview')
        self.addDockWidget(
            QtCore.Qt.LeftDockWidgetArea, self._flow_overview_dock)

        self._flow_overview = flow_overview.FlowOverview()
        self._flow_overview.select_node.connect(self._handle_zoom_to_node)
        self._flow_overview_dock.setWidget(self._flow_overview)
        self._tab_widget.current_flow_changed.connect(
            self._flow_overview.set_flow)
        self._flow_overview.select_flow.connect(
            self.open_flow_window)

    def add_flow_window(self, flow_window_):
        self._tab_widget.open_flow_window_tab(flow_window_)
        self._tab_widget.setCurrentWidget(flow_window_)
        self._menu_manager.set_window_menus(flow_window_)

    def close_flow_window(self, flow_window_):
        return self.close_flow(flow_window_.flow())

    def close_flow(self, flow_):
        """
        Close workflow. If it is a root flow also close the tabs for all
        subflows as well. Make sure to ask the user to save any changes before
        calling this method.
        """
        self._tab_widget.close_flow_tab(flow_)
        self._menu_manager.set_window_menus(self._tab_widget.currentWidget())
        if not flow_.is_subflow():
            self._app_core.remove_flow(flow_)

    def show_flow(self, flow_):
        self._tab_widget.show_flow(flow_)

    @QtCore.Slot(flow_window.FlowWindow)
    def current_flow_changed(self, flow_window_):
        self._menu_manager.set_window_menus(flow_window_)
        if flow_window_:
            filename = flow_window_.flow().root_flow().filename
            if filename != '':
                os.chdir(os.path.dirname(filename))
            else:
                os.chdir(settings.instance()['default_folder'])

            flow_ = flow_window_.flow()
            self._library_view.current_flow_changed(
                flow_ and flow_.root_or_linked_flow())

    def _pre_quit(self):
        if not self._has_quit:
            self._has_quit = True
            settings_ = settings.instance()
            settings_['Gui/geometry'] = self.saveGeometry()
            settings_['Gui/window_state'] = self.saveState()
            if settings_['save_session']:
                flows = self._tab_widget.get_flows()
                files = [flow.filename for flow in flows if flow.filename]
                settings_['session_files'] = files
            flows = self._tab_widget.get_flows()
            root_flows = [f for f in flows if f.flow is None]
            if settings_['ask_for_save']:
                try:
                    common.ask_about_saving_flows(
                        root_flows, include_root=True, discard=True)
                except common.SaveCancelled:
                    self._has_quit = False
            if self._has_quit:
                for f in flows:
                    self._tab_widget.close_flow_tab(f)
                self._stop_docs_builder()
            return not self._has_quit

    @QtCore.Slot()
    def quit_application(self):
        user_cancelled = self._pre_quit()
        if not user_cancelled:
            self.close()

    @QtCore.Slot()
    def show_preferences(self):
        dialog = preferences.PreferencesDialog(
            self._app_core, self._tab_widget.get_current_flow(),
            self._menu_manager, self._preference_widgets, parent=self)
        dialog.exec_()
        self._set_docking_state()
        self._tab_widget.preferences_updated()

    @QtCore.Slot()
    def _show_about_sympathy(self):
        dialog = about_window.AboutWindow(parent=self)
        dialog.exec_()

    @QtCore.Slot()
    def _show_nodewizard(self):
        library_model = library_view.LibraryModel(
            self._app_core.library_root(), self.style(), True)
        wizard = nodewizard.NodeWizard(
            library_model, settings.instance(), self._app_core)
        wizard.exec_()
        if wizard.result() == QtGui.QDialog.Accepted:
            self._app_core.reload_node_library()

    @QtCore.Slot()
    def _show_functionwizard(self):
        functionwizard.FunctionWizard().exec_()

    @QtCore.Slot()
    def _show_librarywizard(self):
        wizard = librarywizard.LibraryWizard()
        wizard.exec_()
        if wizard.result() == QtGui.QDialog.Accepted:
            self._app_core.reload_node_library()
            self._global_library_path_changed()

    @QtCore.Slot(flow.Flow)
    def handle_flow_name_changed(self, flow_):
        self._tab_widget.update_flow_labels()
        if flow_ and flow_.filename:
            os.chdir(os.path.dirname(flow_.filename))

    @QtCore.Slot()
    def reload_library(self):
        self._app_core.reload_node_library()
        self._app_core.restart_workers()

    @QtCore.Slot(six.text_type)
    def open_documentation(self, docs_section):
        """Open a section of the documentation. docs_section should be a path
        to a specific section of the documentation or one of the special values
        'index' or 'node_library'.
        """
        def open_url(doc_path):
            if sys.platform == 'cygwin':
                subprocess.call(['/usr/bin/cygstart', doc_path])
            else:
                doc_url = QtCore.QUrl.fromLocalFile(doc_path)
                doc_url.setScheme('file')
                QtGui.QDesktopServices.openUrl(doc_url)

        doc_path = []
        docs = {
            'index': 'index.html',
            'node_library': 'src/Library/index.html'}
        if docs_section in docs:
            doc_path.append(docs[docs_section])
        else:
            doc_path.append(os.path.join('src', docs_section))

        if len(doc_path) > 0:
            doc_path.insert(0, 'doc/html')
            doc_path.insert(0, settings.instance()['storage_folder'])
            doc_path = nativepath('/'.join(doc_path))

            if os.path.exists(doc_path):
                open_url(doc_path)
            else:
                self._build_docs(functools.partial(
                    open_url, doc_path))

    def _stop_docs_builder(self):
        if self._docs_builder_view:
            self._docs_builder_view.stop()

    def _build_docs(self, callback=None):
        if self._docs_builder_view:
            self._docs_builder_view.stop()

        self._docs_builder_view = DocsBuilderView(
            self._app_core.get_documentation_builder(),
            callback=callback, parent=self)

        self._control_panel.set_current_progress_object(
            self._docs_builder_view)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = file_ids_to_paths(event.mimeData().urls())
            if all(url.toLocalFile().endswith(".syx") for url in urls):
                event.acceptProposedAction()
            else:
                event.setAccepted(False)
        else:
            event.setAccepted(False)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            urls = file_ids_to_paths(event.mimeData().urls())
            for url in urls:
                self.open_named_flow.emit(url.toLocalFile())
        else:
            event.setAccepted(False)

    def closeEvent(self, event):
        user_cancelled = self._pre_quit()
        if not user_cancelled:
            super(MainWindow, self).closeEvent(event)
            event.accept()
        else:
            event.ignore()

    def get_scratch_flow(self):
        return self._tab_widget.get_scratch_flow()

    def _handle_zoom_to_node(self, node):
        # Check with appcore that this node still exists:
        try:
            # TODO (magnus): We need an API in appcore for checking if a node
            # exists. get_node could return None in that case.
            self._app_core.get_node(node.full_uuid)
        except KeyError:
            return

        if node.flow:
            self.open_flow_window.emit(node.flow)
        self._tab_widget.currentWidget()._handle_zoom_to_node(node)

    def _set_docking_state(self):
        state = QtGui.QDockWidget.DockWidgetClosable
        docking = settings.instance()['Gui/docking_enabled']
        movable = True
        floatable = True

        if docking == 'Movable':
            state |= QtGui.QDockWidget.DockWidgetMovable
            floatable = False
        elif docking == 'Locked':
            movable = False
            floatable = False
        else:
            state |= (QtGui.QDockWidget.DockWidgetFloatable |
                      QtGui.QDockWidget.DockWidgetMovable)

        self._library_dock.setFeatures(state)
        self._error_dock.setFeatures(state)
        self._flow_overview_dock.setFeatures(state)

        self._control_panel.setMovable(movable)
        self._control_panel.setFloatable(floatable)


class ProgressObject(QtCore.QObject):

    progress = QtCore.Signal(float)
    done = QtCore.Signal(six.text_type)

    statuses = ('Completed', 'Cancelled', 'Failed', 'In progress')
    (status_complete, status_cancel, status_fail,
     status_in_progress) = statuses

    @property
    def name(self):
        return self._name

    @property
    def desc(self):
        return self._desc

    @property
    def status(self):
        return self._status

    def stop(self):
        pass


class DocsBuilderView(ProgressObject):
    def __init__(self, docs_builder, callback=None, parent=None):
        super(DocsBuilderView, self).__init__(parent)

        self._docs_builder = docs_builder
        self._docs_builder.start()
        self._timer = QtCore.QTimer(parent=parent)
        self._timer.setInterval(100)
        self._timer.timeout.connect(self.update)
        self._timer.start()

        self._name = 'Documenting'
        self._desc = (
            'Building documentation for the platform and all current '
            'libraries.')
        self._status = self.status_in_progress

    @QtCore.Slot()
    def update(self):
        if self._docs_builder.is_alive():
            progress = self._docs_builder.get_progress()
            self.progress.emit(progress)
        else:
            self._timer.stop()
            self._docs_builder.join()
            self.done.emit(self.status_complete)

    def stop(self):
        self._docs_builder.stop()
        self._timer.stop()
        self._callback = None
        self._docs_builder.join()
        self.done.emit(self.status_cancel)
