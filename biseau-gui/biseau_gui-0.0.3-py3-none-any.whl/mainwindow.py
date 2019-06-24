"""Empty docstring"""

import sys
import biseau as bs
import clyngor
import pkg_resources
from collections import defaultdict
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *


from .imageviewer import ImageViewer
from .dotviewer import DotViewer
from .logwidget import LogWidget
from .scriptlistwidget import ScriptListWidget, ScriptRole
from .scripteditor import ScriptEditor
from .scriptbrowser import ScriptBrowserDialog


import time


class MainWindow(QMainWindow):
    def __init__(self, parent=None, default_script:str=None):
        super(MainWindow, self).__init__(parent)
        self.tab_widget = QTabWidget()
        self.log_widget = LogWidget()
        self.script_list_widget = ScriptListWidget()
        self._dock_of_script = defaultdict(list)

        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.addWidget(self.tab_widget)
        self.splitter.addWidget(self.log_widget)
        self.splitter.setStretchFactor(0, 9)
        self.splitter.setStretchFactor(1, 1)
        self.setCentralWidget(self.splitter)

        self.image_viewer = ImageViewer()
        self.dot_viewer = DotViewer(self.image_viewer)

        self.add_central_view(self.image_viewer)
        self.add_central_view(self.dot_viewer)
        # TODO : add more central view

        # Build left script list view
        scripts_dock = QDockWidget()
        scripts_dock.setWindowTitle("Scripts")
        scripts_dock.setWidget(self.script_list_widget)
        scripts_dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(Qt.LeftDockWidgetArea, scripts_dock)

        # setup toolbar and menubar
        self.setup_action()

        # give focus on script editor
        self.script_list_widget.view.itemClicked.connect(
            lambda item: self.set_focus_on_editor(item.data(ScriptRole))
        )

        # Autocompile if script is checked
        self.script_list_widget.view.itemChanged.connect(self.auto_run)

        # (un)comment this to load working scripts
        # self.add_script_from_file("scripts/test_option_types.py")
        self.first_time = True
        if default_script == 'simple':
            self.add_default_script()
        elif default_script == 'gene':
            self.add_script_from_file(pkg_resources.resource_filename(__name__, "embedded_scripts/raw_data.lp"))
            self.add_script_from_file(pkg_resources.resource_filename(__name__, "embedded_scripts/compute_score.py"))
            self.add_script_from_file(pkg_resources.resource_filename(__name__, "embedded_scripts/render_interactions.json"))
        elif default_script == 'init':
            script = self.add_script_from_file(pkg_resources.resource_filename(__name__, "embedded_scripts/context.py"))
            script.options_values['context_file'] = pkg_resources.resource_filename(__name__, "embedded_contexts/human.cxt")
            self.add_script_from_file(pkg_resources.resource_filename(__name__, "embedded_scripts/fca_concepts.lp"))
            self.add_script_from_file(pkg_resources.resource_filename(__name__, "embedded_scripts/fca_lattice.lp"))
        elif default_script == 'FCA':
            script = self.add_script_from_file(pkg_resources.resource_filename(__name__, "embedded_scripts/context.py"))
            script.options_values['context_file'] = pkg_resources.resource_filename(__name__, "embedded_contexts/human.cxt")
            self.add_script_from_file(pkg_resources.resource_filename(__name__, "embedded_scripts/build_concepts.py"))
            self.add_script_from_file(pkg_resources.resource_filename(__name__, "embedded_scripts/build_galois_lattice.json"))
            self.add_script_from_file(pkg_resources.resource_filename(__name__, "embedded_scripts/show_galois_lattice.py"))
        else:
            print('No example loaded. Available examples: simple, gene.')
        self.run()

    def setup_action(self):
        # Setup menu bar
        self.tool_bar = self.addToolBar("main")
        self.tool_bar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        add_script_file_action = self.tool_bar.addAction(
            QIcon.fromTheme("list-add"), "Add script", self.open_script
        )
        add_script_action = self.tool_bar.addAction(
            QIcon.fromTheme("list-add"), "Add default script", self.add_default_script
        )

        # Create Add Menu
        add_menu = QMenu("Add script ...")
        add_menu.addAction(add_script_file_action)
        add_menu.addAction(add_script_action)

        run_action = self.tool_bar.addAction(
            QIcon.fromTheme("media-playback-start"), "Run", self.run
        )
        stop_action = self.tool_bar.addAction(
            QIcon.fromTheme("media-playback-stop"), "Stop", self.stop
        )
        clean_action = self.tool_bar.addAction(
            QIcon.fromTheme("edit-clear"), "Clean Cache", self.clean_cache
        )
        self.auto_run_action = self.tool_bar.addAction(
            QIcon.fromTheme("view-refresh"), "Auto compile"
        )

        add_script_file_action.setShortcut(QKeySequence.Open)
        run_action.setShortcut(Qt.CTRL + Qt.Key_R)
        self.auto_run_action.setCheckable(True)
        self.auto_run_action.triggered.connect(self.set_auto_compile)

        file_menu = self.menuBar().addMenu("&File")
        file_menu.addMenu(add_menu)
        file_menu.addSeparator()
        file_menu.addAction("&Quit", self.close)
        # used to store dock
        # TODO : move dock view elsewhere
        self.view_menu = self.menuBar().addMenu("&View")

        help_menu = self.menuBar().addMenu("&Help")
        help_menu.addAction("About Qt", qApp.aboutQt)

    def add_central_view(self, widget: QWidget):

        self.tab_widget.addTab(widget, widget.windowTitle())

    def open_script(self):
        "Prompt user about a file, try to load a script from it"

        dialog = ScriptBrowserDialog()
        if dialog.exec_():
            for script in dialog.get_scripts():
                self.add_script(script)

    def add_script_from_file(self, filename):
        """add one script into the app. Create list item and dock"""
        # TODO: we should be able to load any script in the file, not only the first
        script = next(bs.module_loader.build_scripts_from_file(filename), None)
        self.add_script(script)
        return script

    def add_script(self, script: bs.Script):
        """add one script into the app. Create list item and dock"""
        # TODO: we should be able to load any script in the file, not only the first
        if not script:
            return
        self.script_list_widget.add_script(script)
        # create dock script editor
        editor = ScriptEditor(script)
        dock = QDockWidget()
        dock.setWindowTitle(script.name)
        dock.setWidget(editor)
        dock.setAllowedAreas(Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        self.view_menu.addAction(dock.toggleViewAction())
        editor.changed.connect(self.auto_run)
        self._dock_of_script[script].append(dock)  # enables to delete it when removing the script
        self.auto_run()

    def add_default_script(self):
        if self.first_time:
            self.add_script_from_file(pkg_resources.resource_filename(__name__, "embedded_scripts/default.lp"))
        else:
            self.add_script_from_file(pkg_resources.resource_filename(__name__, "embedded_scripts/blank.lp"))
        self.first_time = False

    def update_scripts_from_editors(self):
        """ call ScriptEditor.update() on each editor """
        dockWidgets = self.findChildren(QDockWidget)
        for dock in dockWidgets:
            if type(dock.widget()) == ScriptEditor:
                dock.widget().update_script()

    def docks_from_script(self, script: bs.Script):
        """ TODO : dict should be better """
        return self._dock_of_script.get(script, ())

    def set_focus_on_editor(self, script: bs.Script):
        for dock in self.docks_from_script(script):
            # dock.widget().edit_widget.activateWindow()
            dock.widget().edit_widget.setFocus()
            # dock.widget().edit_widget.setFocusPolicy(Qt.StrongFocus)
            # dock.widget().edit_widget.raise_()

    def delete_docks_of_script(self, script: bs.Script):
        for dock in self.docks_from_script(script):
            self.removeDockWidget(dock)


    def run(self):
        """ Run biseau and display the dot file """

        # freeze gui
        self.script_list_widget.setDisabled(True)

        # Update script from editors
        self.update_scripts_from_editors()

        # Run main loop
        try:
            context = ""
            scripts = self.script_list_widget.get_scripts()
            for index, (context, duration) in enumerate(bs.core.yield_run(scripts)):
                self.script_list_widget.set_item_duration(index, duration)
                self.script_list_widget.set_current_script(scripts[index])
                qApp.processEvents()
            self.set_dot(bs.compile_context_to_dot(context))
        except clyngor.utils.ASPSyntaxError as e:
            self.log_widget.add_message(str(e))
        self.script_list_widget.setEnabled(True)

    def auto_run(self):
        if self.auto_run_action.isChecked():
            self.run()

    def stop(self):
        print("STOP")
        # TODO: kill action_run thread

    def clean_cache(self):
        print("CLEAN_CACHE:")
        # TODO : self.scripting_widget.clear_cache()

    def set_auto_compile(self, active: bool):
        print("AUTO_COMPILE:", active)
        # TODO: toggle auto-compilation
        # TODO: change button style

    def set_dot(self, source):
        "Send dot file to the dot viewer for compilation"
        self.dot_viewer.set_dot(source)

    @staticmethod
    def start_gui(*args, **kwargs):
        app = QApplication(sys.argv)
        w = MainWindow(*args, **kwargs)
        w.showMaximized()
        return app.exec_()
