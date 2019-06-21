# /********************************************************************************
# * Copyright © 2018-2019, ETH Zurich, D-BSSE, Andreas P. Cuny & Gotthold Fläschner
# * All rights reserved. This program and the accompanying materials
# * are made available under the terms of the GNU Public License v3.0
# * which accompanies this distribution, and is available at
# * http://www.gnu.org/licenses/gpl
# *
# * Contributors:
# *     Andreas P. Cuny - initial API and implementation
# *******************************************************************************/

import os
import sys
import logging
import pathlib
import ctypes
import webbrowser
import pyqtgraph as pg
from ast import literal_eval
from PyQt5 import uic, QtWidgets, QtCore, QtGui
from PyQt5.Qt import QFileDialog, QMessageBox, QApplication, QStyle, QTextCursor, QPushButton, QListWidget, QSize,\
    QGraphicsSvgItem
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QSettings
from pyIMD.analysis.curve_fit import fit_function
from pyIMD.ui.settings import SettingsDialog
from pyIMD.configuration.defaults import *
from pyIMD.imd import InertialMassDetermination
from pyIMD.ui.table_view_models import PandasDataFrameModel
from concurrent.futures import ThreadPoolExecutor
from pyIMD.ui.resource_path import resource_path
from pyIMD.ui.help import QuickInstructions, ChangeLog, About
from pyIMD.ui.tools import ConcatenateFiles
from pyIMD.__init__ import __version__, __operating_system__
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

__author__ = 'Andreas P. Cuny'


class Stream(QtCore.QObject):
    """
    Implementation of a stream to handle logging messages
    """

    stream_signal = QtCore.pyqtSignal(str)
    """
        pyqtsignal to redirect sterr
    """

    def write(self, text: object) -> object:
        """
            Emits text formatted as string.
            Args:
                text (`str`) Text sent to sterr to be rerouted to the console in the ui.
        """
        self.stream_signal.emit(str(text))


class IMDWindow(QtWidgets.QMainWindow):
    """
    Implementation of the pyIMD main user interface window.
    """

    send_to_console_signal = pyqtSignal(str)
    """
        pyqtSignal used to send a text to the console.
        
    Args:
        message (`str`)         Text to be sent to the console
    """

    def __init__(self):
        super(IMDWindow, self).__init__()
        uic.loadUi(resource_path(os.path.join('ui', 'main_window.ui')), self)
        self.setWindowTitle('pyIMD: Inertial mass determination [build: v%s %s]' % (__version__, __operating_system__))
        self.setWindowIcon(QtGui.QIcon(resource_path(os.path.join(os.path.join("ui", "icons",
                                                                               "pyIMD_logo_icon.ico")))))

        # Add AppUserModelID for windows systems
        if sys.platform == 'win32':
            app_id = u'ethz.csb.pyCAME.v%s' % __version__
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

        # Init QSettings for cross-platform temp settings file in ini format
        self.settings = QSettings(QSettings.IniFormat, QSettings.SystemScope, 'CSB', 'pyIMD')

        self.menuBar.setNativeMenuBar(False)
        self.settings_dialog = None
        self.about_window = None
        self.file_list = []
        self.current_batch_project_file = []
        self.last_selected_path = ''
        self.show()
        self.console_edit.setReadOnly(True)
        self.radio_btn_name_array = ['autoRadio', 'pllRadio', 'contSweepRadio']
        self.opening_mode = 0 # intended to be used to distinguish if the ui is started as stand alone or not.
        self.task_done = False
        self.executor = ThreadPoolExecutor(max_workers=4)

        # Settings
        self.__settings = {"figure_format": FIGURE_FORMAT,
                           "figure_width": FIGURE_WIDTH,
                           "figure_height": FIGURE_HEIGHT,
                           "figure_units": FIGURE_UNITS,
                           "figure_resolution_dpi": FIGURE_RESOLUTION_DPI,
                           "figure_name_pre_start_no_cell": FIGURE_NAME_PRE_START_NO_CELL,
                           "figure_name_pre_start_with_cell": FIGURE_NAME_PRE_START_WITH_CELL,
                           "figure_name_measured_data": FIGURE_NAME_MEASURED_DATA,
                           "figure_plot_every_nth_point": FIGURE_PLOT_EVERY_NTH_POINT,
                           "conversion_factor_hz_to_khz": CONVERSION_FACTOR_HZ_TO_KHZ,
                           "conversion_factor_deg_to_rad": CONVERSION_FACTOR_DEG_TO_RAD,
                           "spring_constant": SPRING_CONSTANT,
                           "cantilever_length": CANTILEVER_LENGTH,
                           "cell_position": CELL_POSITION,
                           "initial_parameter_guess": INITIAL_PARAMETER_GUESS,
                           "lower_parameter_bounds": LOWER_PARAMETER_BOUNDS,
                           "upper_parameter_bounds": UPPER_PARAMETER_BOUNDS,
                           "rolling_window_size": ROLLING_WINDOW_SIZE,
                           "correct_for_frequency_offset": CORRECT_FOR_FREQUENCY_OFFSET,
                           "frequency_offset_mode": FREQUENCY_OFFSET_MODE,
                           "frequency_offset_n_measurements_used": FREQUENCY_OFFSET_N_MEASUREMENTS_USED,
                           "frequency_offset": FREQUENCY_OFFSET,
                           "read_text_data_from_line": READ_TEXT_DATA_FROM_LINE,
                           "text_data_delimiter": repr(TEXT_DATA_DELIMITER).replace("'", "")}

        self.settings_dialog = SettingsDialog(self.__settings)
        self.settings_dialog.settings_has_changed_signal.connect(
            self.on_settings_changed)
        self.settings_dialog.set_values()
        self.setup_console_connection()
        self.selectDirBtn.clicked.connect(self.select_data_files)
        self.selectDirBtn.setShortcut("Ctrl+N")

        data_items = ['Measured data', 'Pre start no cell data', 'Pre start with cell data', 'Pre start frequency shift',
                      'Calculated cell mass']
        for i in range(0, len(data_items)):
            self.dataList.addItem(str(data_items[i]))
        self.dataList.itemSelectionChanged.connect(self.on_data_list_selection_changed)
        self.noCellDataBox.currentIndexChanged.connect(self.on_combo_box_changed)
        self.withCellDataBox.currentIndexChanged.connect(self.on_combo_box_changed)
        self.measuredDataBox.currentIndexChanged.connect(self.on_combo_box_changed)
        self.runCalculationBtn.clicked.connect(self.run_calculation)
        self.projectFilesBtn.clicked.connect(self.select_batch_files)
        self.runBatchBtn.clicked.connect(self.run_batch_calculation)

        self.actionView_Console.setIcon(QApplication.style().standardIcon(QStyle.SP_DialogApplyButton))
        self.actionView_Console.setShortcut("Ctrl+C")
        self.actionView_Console.setStatusTip('Show / hide console console')
        self.actionView_Console.triggered.connect(self.show_console)

        self.actionQuit.setIcon(QApplication.style().standardIcon(QStyle.SP_DialogCloseButton))
        self.actionQuit.setShortcut("Ctrl+Q")
        self.actionQuit.setStatusTip('Quit the application')
        self.actionQuit.triggered.connect(self.close_application)

        self.actionSave_project.setIcon(QApplication.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.actionSave_project.setShortcut("Ctrl+S")
        self.actionSave_project.setStatusTip('Save a pyIMD project')
        self.actionSave_project.triggered.connect(self.save_project)

        self.actionOpen_project.setIcon(QApplication.style().standardIcon(QStyle.SP_DirOpenIcon))
        self.actionOpen_project.setShortcut("Ctrl+O")
        self.actionOpen_project.setStatusTip('Open a pyIMD project')
        self.actionOpen_project.triggered.connect(self.open_project)

        self.actionSettings.setIcon(QApplication.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        self.actionSettings.setShortcut("Ctrl+P")
        self.actionSettings.setStatusTip('Configure pyIMD calculation settings')
        self.actionSettings.triggered.connect(self.show_settings_dialog)

        tools_menu = self.menuBar.addMenu('Tools')
        action_concat = tools_menu.addAction("Concatenate files")
        self.concatenation = ConcatenateFiles()
        action_concat.triggered.connect(self.on_concatenation)

        self.about_window = About()
        self.actionAbout.setShortcut("Ctrl+A")
        self.actionAbout.triggered.connect(self.on_about)

        self.qi = QuickInstructions()
        self.actionQuick_instructions.setStatusTip('Hints about how to use this program')
        self.actionQuick_instructions.triggered.connect(self.on_quick_instructions)

        self.change_log = ChangeLog()
        self.actionChange_log.setStatusTip('See what change recently')
        self.actionChange_log.triggered.connect(self.on_change_log)

        self.actionRead_documentation.setStatusTip('Show online documentation')
        self.actionRead_documentation.triggered.connect(self.on_read_documentation)

        sys.stderr = Stream(stream_signal=self.on_update_text)

        self.batchFileListWidget.setSelectionMode(QListWidget.MultiSelection)
        self.tabWidget.setTabEnabled(2, False)
        self.tabWidget.setCurrentIndex(0)

        self.graphicsView.plotItem.ctrlMenu = None
        self.imd_icon = QGraphicsSvgItem(resource_path(os.path.join(os.path.join("ui", "icons", "pyIMD_logo_vect.svg"))))
        self.imd_icon.scale(1, -1)

        self.graphicsView.addItem(self.imd_icon)
        self.graphicsView.hideAxis('bottom')
        self.graphicsView.hideAxis('left')

        self.logger = self.get_logger_object(__name__)
        self.logger.setLevel(logging.INFO)

        self.imd = InertialMassDetermination()

        try:
            if self.settings.value('display_on_startup') is None:
                self.settings.setValue('display_on_startup', 2)
                self.qi.show()

            elif int(self.settings.value('display_on_startup')) == 2:
                self.qi.show()
        except Exception as e:
            self.print_to_console('Could not load quick instruction window due to corrupt settings.ini file' + str(e))

    @staticmethod
    def on_read_documentation():
        """
        Opens the documentation in the default web browser.
        """
        webbrowser.open('https://pyimd.readthedocs.io/en/latest/')

    def on_change_log(self):
        """
        Displays the change log window.
        """
        self.change_log.show()

    def on_quick_instructions(self):
        """
        Displays the quick instructions window.
        """
        self.qi.show()

    def on_about(self):
        """
        Displays the about window.
        """
        self.about_window.show()

    def on_concatenation(self):
        """
        Opens concatenation dialog and starts file concatenation in new thread.
        """
        try:
            directory, time_interval, dialog_state = self.concatenation.get_user_input()
            if dialog_state:
                self.executor.submit(self.imd.concatenate_files, directory, time_interval=time_interval)
        except Exception as e:
            self.print_to_console("Concatenation aborted by user: ")

    def on_update_text(self, text):
        """
        Writes new text to the console at the last text cursor position

        Args:
            text (`str`):   Text to be shown on the console.
        """
        cursor = self.console_edit.textCursor()
        cursor.movePosition(QTextCursor.NoMove)
        cursor.insertText(text)
        self.console_edit.setTextCursor(cursor)
        self.console_edit.ensureCursorVisible()

    def show_console(self):
        """
        Show and hide the console with the program log.
        """
        if self.consoleDock.isVisible():
            self.consoleDock.hide()
            self.actionView_Console.setIcon(QApplication.style().standardIcon(QStyle.SP_DialogCancelButton))
        else:
            self.consoleDock.show()
            self.actionView_Console.setIcon(QApplication.style().standardIcon(QStyle.SP_DialogApplyButton))

    def run_calculation(self):
        """
        Implementation of the pyIMD calculation start as new thread.
        """
        if self.autoRadio.isChecked():
            self.print_to_console("Auto mode not implemented yet: ")
        elif self.contSweepRadio.isChecked():
            self.print_to_console("Sweep mode starting...")
            self.print_to_console('')  # Needed to output logging information to newline in console

            self.sync_settings()

            task = self.executor.submit(self.imd.run_inertial_mass_determination)
            task.add_done_callback(self.on_task_finished)

        elif self.pllRadio.isChecked():
            self.print_to_console("PLL mode starting...")
            self.print_to_console('')  # Needed to output logging information to newline in console

            self.sync_settings()

            task = self.executor.submit(self.imd.run_inertial_mass_determination)
            task.add_done_callback(self.on_task_finished)

    def on_task_finished(self, task):
        """
        Enable the Result tab after the inertial mass determination run is finished.

        Args:
        task:  ThreadPoolExecutor task
        """
        self.tabWidget.setTabEnabled(2, True)
        self.settings_dialog.frequency_offset_edit.setText(str(self.imd.settings.frequency_offset))
        self.task_done = True

    def run_batch_calculation(self):
        """
        Implementation of the pyIMD calculation batch mode based on pyIMD project files.
        """
        selected_project_files = []
        for item in self.batchFileListWidget.selectedItems():
            selected_project_files.append(item.text())

        if len(selected_project_files) != 0:
            self.print_to_console("Batch calculation mode starting...")
            for iProject in range(0, len(selected_project_files)):
                self.current_batch_project_file = selected_project_files[iProject]  # here iterate over project files
                self.print_to_console(self.current_batch_project_file)
                # 1. Open Project from list
                self.open_project()
                # 2. Run calculation
                self.run_calculation()
                # 3. Get signal that it is done
                # Start next project

    def on_combo_box_changed(self, index):
        """
        Prints the selected item of the data drop down list to the console.

        Args:
            index (`int`): Index of the selected item from the drop down list.

        """
        sender = self.sender().objectName()
        if sender == 'noCellDataBox':
            # self.imd.settings.pre_start_no_cell_path = self.file_list[index]
            self.print_to_console("Pre start no cell file selected:" + self.file_list[index])
        elif sender == 'withCellDataBox':
            # self.imd.settings.pre_start_with_cell_path = self.file_list[index]
            self.print_to_console("Pre start with cell file selected:" + self.file_list[index])
        elif sender == 'measuredDataBox':
            # self.imd.settings.measurements_path = self.file_list[index]
            self.print_to_console("Measurement file selected:" + self.file_list[index])

    def on_data_list_selection_changed(self):
        """
        Adds the selected data to the PandasDataFrameModel model to be displayed in the results table view.
        """
        item = self.dataList.selectedItems()[0]
        try:
            if item.text() == 'Measured data':
                # Display data
                model = PandasDataFrameModel(self.imd.data_measured)
                self.tableView.setModel(model)
                # Notify user about selection
                self.print_to_console("Displaying: " + item.text())

            elif item.text() == 'Pre start no cell data':
                # Display data
                model = PandasDataFrameModel(self.imd.data_pre_start_no_cell)
                self.tableView.setModel(model)
                self.graphicsView.clear()
                self.graphicsView.plot(self.imd.data_pre_start_no_cell.iloc[:, 0],
                                       self.imd.data_pre_start_no_cell.iloc[:, 2], pen=None, symbol='o',
                                       symbolPen=pg.hsvColor(0, 0, 0, 0.1), symbolBrush=pg.hsvColor(0, 0, 0, 0.1))
                y_fit = fit_function(self.imd.data_pre_start_no_cell.iloc[:, 0],
                                     self.imd.resonance_freq_pre_start_no_cell, self.imd.fit_param_pre_start_no_cell[0],
                                     self.imd.fit_param_pre_start_no_cell[1], self.imd.fit_param_pre_start_no_cell[2])
                self.graphicsView.plot(self.imd.data_pre_start_no_cell.iloc[:, 0], y_fit, pen=pg.mkPen('r', width=1.5))
                self.graphicsView.setLabel('bottom', 'Frequency (kHz)')
                self.graphicsView.setLabel('left', 'Phase (rad)')
                self.graphicsView.showGrid(x=True, y=True)
                # Notify user about selection
                self.print_to_console("Displaying: " + item.text())

            elif item.text() == 'Pre start with cell data':
                # Display data
                model = PandasDataFrameModel(self.imd.data_pre_start_with_cell)
                self.tableView.setModel(model)
                self.graphicsView.clear()
                self.graphicsView.plot(self.imd.data_pre_start_with_cell.iloc[:, 0],
                                       self.imd.data_pre_start_with_cell.iloc[:, 2], pen=None, symbol='o',
                                       symbolPen=pg.hsvColor(0, 0, 0, 0.1), symbolBrush=pg.hsvColor(0, 0, 0, 0.1))
                y_fit = fit_function(self.imd.data_pre_start_with_cell.iloc[:, 0],
                                     self.imd.resonance_freq_pre_start_with_cell, self.imd.fit_param_pre_start_with_cell[0],
                                     self.imd.fit_param_pre_start_with_cell[1], self.imd.fit_param_pre_start_with_cell[2])
                self.graphicsView.plot(self.imd.data_pre_start_with_cell.iloc[:, 0], y_fit, pen=pg.mkPen('r', width=1.5))
                self.graphicsView.setLabel('bottom', 'Frequency (kHz)')
                self.graphicsView.setLabel('left', 'Phase (rad)')
                self.graphicsView.showGrid(x=True, y=True)
                # Notify user about selection
                self.print_to_console("Displaying: " + item.text())

            elif item.text() == 'Pre start frequency shift':
                # Display data
                model = PandasDataFrameModel(self.imd.data_pre_start_no_cell)# Try to fuse the dfs first to one table
                self.tableView.setModel(model)
                self.graphicsView.clear()
                y_fit_without = fit_function(self.imd.data_pre_start_no_cell.iloc[:, 0],
                                     self.imd.resonance_freq_pre_start_no_cell, self.imd.fit_param_pre_start_no_cell[0],
                                     self.imd.fit_param_pre_start_no_cell[1], self.imd.fit_param_pre_start_no_cell[2])
                y_fit_with = fit_function(self.imd.data_pre_start_with_cell.iloc[:, 0],
                                     self.imd.resonance_freq_pre_start_with_cell, self.imd.fit_param_pre_start_with_cell[0],
                                     self.imd.fit_param_pre_start_with_cell[1], self.imd.fit_param_pre_start_with_cell[2])

                self.graphicsView.plot(self.imd.data_pre_start_no_cell.iloc[:, 0],
                                       self.imd.data_pre_start_no_cell.iloc[:, 2], pen=None, symbol='o',
                                       symbolPen=pg.hsvColor(0, 0, 0, 0.1), symbolBrush=pg.hsvColor(0, 0, 0, 0.1),
                                       name="Raw phase w/o cell")
                self.graphicsView.plot(self.imd.data_pre_start_no_cell.iloc[:, 0], y_fit_without,
                                       pen=pg.mkPen('r', width=1.5), name="Phase fit w/ cell attached")
                self.graphicsView.plot(self.imd.data_pre_start_with_cell.iloc[:, 0],
                                       self.imd.data_pre_start_with_cell.iloc[:, 2], pen=None, symbol='o',
                                       symbolPen=pg.hsvColor(0, 0, 0, 0.1), symbolBrush=pg.hsvColor(0, 0, 0, 0.1),
                                       name="Raw phase w/ cell")
                self.graphicsView.plot(self.imd.data_pre_start_with_cell.iloc[:, 0], y_fit_with,
                                       pen=pg.mkPen('c', width=1.5), name="Phase fit w/o cell attached")
                self.graphicsView.setLabel('bottom', 'Frequency (kHz)')
                self.graphicsView.setLabel('left', 'Phase (rad)')
                self.graphicsView.showGrid(x=True, y=True)
                # Notify user about selection
                self.print_to_console("Displaying: " + item.text())

            elif item.text() == 'Calculated cell mass':
                # Display data
                model = PandasDataFrameModel(self.imd.calculated_cell_mass)
                self.tableView.setModel(model)
                self.graphicsView.clear()
                self.graphicsView.plot(self.imd.calculated_cell_mass.iloc[::10, 0],
                                       self.imd.calculated_cell_mass.iloc[::10, 1], pen=None, symbol='o',
                                       symbolPen=pg.hsvColor(0, 0, 0, 0.1), symbolBrush=pg.hsvColor(0, 0, 0, 0.1),
                                       name="Measured cell mass")
                self.graphicsView.plot(self.imd.calculated_cell_mass.iloc[:, 0],
                                       self.imd.calculated_cell_mass.iloc[:, 2], pen=pg.mkPen('r', width=1.5),
                                       name="Mean measured cell mass")
                self.graphicsView.setLabel('bottom', 'Time (h)')
                self.graphicsView.setLabel('left', 'Mass (ng)')
                self.graphicsView.showGrid(x=True, y=True)
                # Notify user about selection
                self.print_to_console("Displaying: " + item.text())
            else:
                return
        except Exception as e:
            self.print_to_console("Error no pyIMD object yet. Please run calculation first: " + str(e))

    def select_data_files(self):
        """
        Select data files to create a new pyIMD project
        """
        try:
            filter_ext = "All files (*.*);; Txt (*.txt);; TDMS (*.tdms);; All files " \
                         "without file endings (*)"
            file_name = QFileDialog()
            file_name.setFileMode(QFileDialog.ExistingFiles)
            ret = file_name.getOpenFileNames(self, "Pick relevant data files",
                                             self.last_selected_path, filter_ext)
            names = ret[0]
            if len(names) > 0:
                # Clear previous file list
                self.file_list = []
                # Setting the file list
                self.file_list = names
                sorted_file_list = self.file_list
                self.last_selected_path = os.path.dirname(sorted_file_list[0])
                self.show_data()
                self.print_to_console("Selected %d files." % (len(sorted_file_list)))

                # Populate drop down list with selected items.
                self.noCellDataBox.clear()
                self.withCellDataBox.clear()
                self.measuredDataBox.clear()
                self.noCellDataBox.addItems(self.file_list)
                self.withCellDataBox.addItems(self.file_list)
                self.measuredDataBox.addItems(self.file_list)
                # Create new pyimd project
                self.imd.create_pyimd_project(self.file_list[0], self.file_list[0], self.file_list[0], '\t', 23, 'PLL')
        except Exception as e:
            self.print_to_console("Error could not select files." + str(e))

    def select_batch_files(self):
        """
        Selection of .xml pyIMD project files for batch calculation.
        """
        filter_ext = "XML (*.xml);;, All files (*.*) "
        file_name = QFileDialog()
        file_name.setFileMode(QFileDialog.ExistingFiles)
        ret = file_name.getOpenFileNames(self, "Select the pyIMD project files for batch processing",
                                         self.last_selected_path, filter_ext)
        files = ret[0]
        for i in range(0, len(files)):
            self.batchFileListWidget.addItem(str(files[i]))

    def show_data(self):
        """
        Display the selected file names om the file viewer.
        """
        model = QtGui.QStandardItemModel(len(self.file_list), 0)

        for row, label in enumerate(self.file_list):
            p = pathlib.Path(label)
            item = QtGui.QStandardItem(p.stem)
            model.setItem(row, 0, item)
        self.tableViewSelData.setModel(model)
        self.tableViewSelData.horizontalHeader().setStretchLastSection(True)
        self.tableViewSelData.horizontalHeader().hide()

    def show_settings_dialog(self):
        """
        Show the settings dialog.
        """
        if self.settings_dialog is None:
            self.settings_dialog = SettingsDialog(self.__settings)
            self.settings_dialog.settings_has_changed_signal.connect(
                self.on_settings_changed)

        self.settings_dialog.exec()

    @pyqtSlot(dict, name="settings_has_changed_signal")
    def on_settings_changed(self, changed_settings):
        """
        Update settings from settings dialog to settings configuration as soon as user commits parameter changes.

        Args:
            changed_settings (`dict`):  Settings dictionary

        Returns:
            Null (`void`):              Updates the changed settings on the object directly
        """
        # Update the settings of the ui
        self.__settings = changed_settings
        # Update the settings of the imd object
        self.sync_settings()

    def sync_settings(self):
        """
        Synchronizes the settings of the UI with the pyIMD object settings object.
        """
        try:
            # Parameter settings
            self.imd.settings.figure_width = float(self.__settings["figure_width"])
            self.imd.settings.figure_height = float(self.__settings["figure_height"])
            self.imd.settings.figure_units = str(self.__settings["figure_units"])
            self.imd.settings.figure_format = str(self.__settings["figure_format"])
            self.imd.settings.figure_resolution_dpi = int(self.__settings["figure_resolution_dpi"])
            self.imd.settings.figure_name_pre_start_no_cell = self.__settings["figure_name_pre_start_no_cell"]
            self.imd.settings.figure_name_pre_start_with_cell = self.__settings["figure_name_pre_start_with_cell"]
            self.imd.settings.figure_name_measured_data = self.__settings["figure_name_measured_data"]
            self.imd.settings.figure_plot_every_nth_point = int(self.__settings["figure_plot_every_nth_point"])
            self.imd.settings.conversion_factor_hz_to_khz = float(self.__settings["conversion_factor_hz_to_khz"])
            self.imd.settings.conversion_factor_deg_to_rad = float(self.__settings["conversion_factor_deg_to_rad"])
            self.imd.settings.spring_constant = float(self.__settings["spring_constant"])
            self.imd.settings.cantilever_length = float(self.__settings["cantilever_length"])
            self.imd.settings.cell_position = float(self.__settings["cell_position"])

            if type(self.__settings["initial_parameter_guess"]) == str:
                self.imd.settings.initial_parameter_guess = literal_eval(self.__settings["initial_parameter_guess"])
            else:
                self.imd.settings.initial_parameter_guess = self.__settings["initial_parameter_guess"]

            if type(self.__settings["lower_parameter_bounds"]) == str:
                self.imd.settings.lower_parameter_bounds = literal_eval(self.__settings["lower_parameter_bounds"])
            else:
                self.imd.settings.lower_parameter_bounds = self.__settings["lower_parameter_bounds"]

            if type(self.__settings["upper_parameter_bounds"]) == str:
                self.imd.settings.upper_parameter_bounds = literal_eval(self.__settings["upper_parameter_bounds"])
            else:
                self.imd.settings.upper_parameter_bounds = self.__settings["upper_parameter_bounds"]

            self.imd.settings.rolling_window_size = int(self.__settings["rolling_window_size"])
            self.imd.settings.correct_for_frequency_offset = self.__settings["correct_for_frequency_offset"]
            self.imd.settings.frequency_offset_mode = str(self.__settings["frequency_offset_mode"])
            self.imd.settings.frequency_offset_n_measurements_used = float(self.__settings[
                                                                               "frequency_offset_n_measurements_used"])
            self.imd.settings.frequency_offset = float(self.__settings["frequency_offset"])
            self.imd.settings.read_text_data_from_line = int(self.__settings["read_text_data_from_line"])
            self.imd.settings.text_data_delimiter = str(self.__settings["text_data_delimiter"])
            # Project settings
            self.imd.settings.selected_files = self.file_list

            for i in range(0, len(self.radio_btn_name_array)):
                radio_name = getattr(self, self.radio_btn_name_array[i])
                if radio_name.isChecked():
                    self.imd.settings.calculation_mode = radio_name.text()

            self.imd.settings.pre_start_no_cell_path = self.noCellDataBox.currentText()
            self.imd.settings.pre_start_with_cell_path = self.withCellDataBox.currentText()
            self.imd.settings.measurements_path = self.measuredDataBox.currentText()

        except Exception as e:
            self.print_to_console("Error during settings synchronization: " + str(e))

    def setup_console_connection(self):
        """
        Set up the console connection between the settings and the main window.
        """
        self.settings_dialog.send_to_console_signal.connect(self.handle_change_console_text)

    def print_to_console(self, text):
        """
        Print text to console.

        Args:
            text (`str`)        Text to be printed to the console.
        """
        self.logger.info(text)

    @pyqtSlot(str, name="handle_change_console_text")
    def handle_change_console_text(self, text):
        """
        Implementation of the handle_change_console_text slot.

        Args:
            text (`str`):       String received from Settings instance to print to the console.
        """
        self.print_to_console(text)

    def save_project(self):
        """
        Saves a pyIMD project file as .xml using the IntertialMassDetermination.save_pyimd_project method

        Returns:
            Null (`void`):      Saves pyIMD project as xml file to disk
        """

        file_dialog = QFileDialog()
        project_file_dir = file_dialog.getSaveFileName(self)

        if len(project_file_dir[0]) > 0:
            try:
                # Make sure all ui settings are in sync with imd settings.
                self.sync_settings()

                self.imd.save_pyimd_project(project_file_dir[0])

                self.print_to_console("Project saved successfully")
            except Exception as e:
                self.print_to_console("Error during saving project: " + str(e))
        else:
            self.print_to_console("Project saving aborted by user")

    def open_project(self):
        """
        Opens a pyIMD project file (.xml) using the IntertialMassDetermination.load_pyimd_project method
        """

        # Quick hack to distinguish action depending on sender
        if self.sender().objectName() == 'actionOpen_project':

            project_filter_ext = "XML (*.xml);; All files (*.*)"
            file_dialog = QFileDialog()
            file_dialog.setFileMode(QFileDialog.ExistingFiles)
            selected_project_file = file_dialog.getOpenFileName(self, "Select a pyIMD project file",
                                                                self.last_selected_path, project_filter_ext)
        else:
            selected_project_file = [self.current_batch_project_file]

        if len(selected_project_file[0]) > 0:
            try:
                # Load pyimd project
                self.imd.load_pyimd_project(selected_project_file[0])

                # Update ui.Settings with parameters:
                self.__settings = {"figure_format": self.imd.settings.figure_format,
                                   "figure_width": self.imd.settings.figure_width,
                                   "figure_height": self.imd.settings.figure_height,
                                   "figure_units": self.imd.settings.figure_units,
                                   "figure_resolution_dpi": self.imd.settings.figure_resolution_dpi,
                                   "figure_name_pre_start_no_cell": self.imd.settings.figure_name_pre_start_no_cell,
                                   "figure_name_pre_start_with_cell": self.imd.settings.figure_name_pre_start_with_cell,
                                   "figure_name_measured_data": self.imd.settings.figure_name_measured_data,
                                   "figure_plot_every_nth_point": self.imd.settings.figure_plot_every_nth_point,
                                   "conversion_factor_hz_to_khz": self.imd.settings.conversion_factor_hz_to_khz,
                                   "conversion_factor_deg_to_rad": self.imd.settings.conversion_factor_deg_to_rad,
                                   "spring_constant": self.imd.settings.spring_constant,
                                   "cantilever_length": self.imd.settings.cantilever_length,
                                   "cell_position": self.imd.settings.cell_position,
                                   "initial_parameter_guess": self.imd.settings.initial_parameter_guess,
                                   "lower_parameter_bounds": self.imd.settings.lower_parameter_bounds,
                                   "upper_parameter_bounds": self.imd.settings.upper_parameter_bounds,
                                   "rolling_window_size": self.imd.settings.rolling_window_size,
                                   "correct_for_frequency_offset": self.imd.settings.correct_for_frequency_offset,
                                   "frequency_offset_mode": self.imd.settings.frequency_offset_mode,
                                   "frequency_offset_n_measurements_used": self.imd.settings.frequency_offset_n_measurements_used,
                                   "frequency_offset": self.imd.settings.frequency_offset,
                                   "read_text_data_from_line": self.imd.settings.read_text_data_from_line,
                                   "text_data_delimiter": self.imd.settings.text_data_delimiter}
                self.settings_dialog.__init__(self.__settings)
                self.settings_dialog.set_values()

                # Update ui with loaded data:
                self.last_selected_path = self.imd.settings.project_folder_path.replace("\\", "/")

                self.file_list = []
                for i in range(0, len(self.imd.settings.selected_files)):
                    self.file_list.append(pathlib.Path().joinpath(self.last_selected_path,
                                                                  self.imd.settings.selected_files[i]).as_posix())
                self.show_data()
                self.noCellDataBox.clear()
                self.noCellDataBox.addItems(self.file_list)
                index = self.noCellDataBox.findText(self.imd.settings.pre_start_no_cell_path.replace("\\", "/"),
                                                    QtCore.Qt.MatchFixedString)
                if index >= 0:
                    self.noCellDataBox.setCurrentIndex(index)

                self.withCellDataBox.clear()
                self.withCellDataBox.addItems(self.file_list)
                index = self.withCellDataBox.findText(self.imd.settings.pre_start_with_cell_path.replace("\\", "/"),
                                                      QtCore.Qt.MatchFixedString)
                if index >= 0:
                    self.withCellDataBox.setCurrentIndex(index)
                self.measuredDataBox.clear()
                self.measuredDataBox.addItems(self.file_list)
                index = self.measuredDataBox.findText(self.imd.settings.measurements_path.replace("\\", "/"),
                                                      QtCore.Qt.MatchFixedString)
                if index >= 0:
                    self.measuredDataBox.setCurrentIndex(index)

                for i in range(0, len(self.radio_btn_name_array)):
                    radio_name = getattr(self, self.radio_btn_name_array[i])
                    if radio_name.text() == self.imd.settings.calculation_mode:
                        radio_name.setChecked(True)

                self.print_to_console("Project {} successfully opened".format(pathlib.Path(
                    selected_project_file[0]).name))
            except Exception as e:
                self.print_to_console("Error during opening project in UI: " + str(e))
        else:
            self.print_to_console("Project opening aborted by user")

    @staticmethod
    def get_logger_object(name):
        """
        Gets a logger object to log messages of pyIMD status to the console in a standardized format.

        Returns:
            logger (`object`):      Returns a logger object with correct string formatting.
        """
        logger = logging.getLogger(name)
        if not logger.handlers:
            # Prevent logging from propagating to the root logger
            logger.propagate = 0
            console = logging.StreamHandler(sys.stderr)
            logger.addHandler(console)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            console.setFormatter(formatter)
            logger.setLevel(logging.INFO)

        return logger

    def close_application(self, event):
        """
        Opens a message box to handle program exit properly asking the user if the project should be saved first.

        Args:
            event(`QCloseEvent`):                   A QCloseEvent

        Returns:
            status_code (`int`):                    0 when process finished correctly, otherwise >0
        """
        self.settings.setValue('display_on_startup', self.qi.display_on_startup)

        msg_box = QMessageBox()
        msg_box.setWindowIcon(QtGui.QIcon(resource_path(os.path.join("ui", "icons", "pyIMD_logo_icon.ico"))))
        msg_box.setWindowTitle('pyIMD :: Quit Program')
        msg_box.setText('Do you want to save changes before quitting the program?')
        save_btn = QPushButton('Save')
        save_btn.setIcon(QApplication.style().standardIcon(QStyle.SP_DialogSaveButton))
        msg_box.addButton(save_btn, QMessageBox.YesRole)
        no_save_btn = QPushButton('Don\'t save')
        no_save_btn.setIcon(QApplication.style().standardIcon(QStyle.SP_DialogNoButton))
        msg_box.addButton(no_save_btn, QMessageBox.NoRole)
        abort_btn = QPushButton('Cancel')
        abort_btn.setIcon(QApplication.style().standardIcon(QStyle.SP_DialogCancelButton))
        msg_box.addButton(abort_btn, QMessageBox.RejectRole)
        ret = msg_box.exec_()

        if ret == 0:
            self.save_project()
            if not event:
                self.close()
            else:
                event.accept()
        elif ret == 1:
            if not event:
                self.close()
            else:
                event.accept()
        else:
            self.print_to_console("Program quit aborted")
            if not event:
                return
            else:
                event.ignore()

    def closeEvent(self, event):
        """
        Application close event override of QMainWindow closeEvent

        Args:
            event (`QCloseEvent`):                  A QCloseEvent

        Returns:
            status_code (`int`):                   O when process finished correctly otherwise >0
        """
        self.close_application(event)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = IMDWindow()
    app_icon = QtGui.QIcon()
    app_icon.addFile(resource_path(os.path.join("icons", "pyIMD_logo_icon.ico")), QSize(256, 256))
    app.setWindowIcon(app_icon)
    sys.exit(app.exec_())
