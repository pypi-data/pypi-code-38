# -*- coding: utf-8 -*-

"""package fft_dev
brief     UI Form of FFT program.
author    Benoit Dubois
copyright FEMTO Engineering, 2019
licence   GPL3+
"""

import logging
import ntpath
import os.path as path

from PyQt5 import QtCore, QtWidgets, QtGui

import pyqtgraph as pg
from pyqtgraph.parametertree import Parameter, ParameterTree
from pyqtgraph.parametertree.parameterTypes import TextParameter

from fft_dev.fft35670a.fft35670a_dev_prologix import \
    LOG_FREQ_START_MAP, LOG_FREQ_STOP_MAP, VOLT_MAP, \
    XAXIS_UNIT_MAP, YAXIS_UNIT_MAP, YAXIS_FORMAT_MAP, \
    INPUT_COUPLING, INPUT_IMPEDANCE, \
    AVERAGE_TYPE_MAP, AVERAGE_NUMBER_LIMITS, \
    SOURCE_SHAPE_MAP, SOURCE_LEVEL_VRMS_LIMITS, SOURCE_OFFSET_LIMITS

# Use white background and black foreground
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

APP_NAME = "FFT acquisition"
LEGEND_FORMAT = ':.'

MEASUREMENT_MAP = {
    "Frequency response": "\'XFR:POW:RAT 1,2\'",
    "Power spectrum 1": "\'XFR:POW 1\'",
    "Power spectrum 2": "\'XFR:POW 2\'",
    "Cross spectrum": "\'XFR:POW:CROS 1,2\'"
}

IO_PARAM = {'name': 'IO parameters', 'type': 'group', 'children': [
    {'name': 'Choose workspace', 'type': 'action', 'children': [
        {'name': 'Working directory', 'type': 'str', 'readonly': True}
    ]},
    {'name': 'Filename', 'type': 'str', 'value': '', 'readonly': True}
]}

AVERAGE_PARAM = [
    {'name': 'Enable', 'type': 'bool', 'value': False,
     'tip': "Enable/Disable averaging"},
    {'name': 'Mode', 'type': 'list', 'values': AVERAGE_TYPE_MAP.keys(),
     'value': 'RMS'},
    {'name': 'Count', 'type': 'int',
     'limits': AVERAGE_NUMBER_LIMITS, 'default': 1}
]

ACQ_PARAM = {'name': 'Acquisition', 'type': 'group', 'children': [
    # {'name': 'Major mode', 'type': 'list', 'values': MAJOR_MODE_MAP.keys()},
    {'name': 'Measurement', 'type': 'list', 'values': MEASUREMENT_MAP.keys(),
     'value': 'Power spectrum 1'},
    {'name': 'Start', 'type': 'list', 'values': LOG_FREQ_START_MAP.keys(),
     'value': '10 Hz'},
    {'name': 'Stop', 'type': 'list', 'values': LOG_FREQ_STOP_MAP.keys(),
     'value': '100 kHz'},
    {'name': 'Averaging', 'type': 'group', 'children': AVERAGE_PARAM}
]}

DISPLAY_PARAM = {'name': 'Display', 'type': 'group', 'children': [
    {'name': 'X axis', 'type': 'group', 'children': [
        {'name': 'Units', 'type': 'list', 'values': XAXIS_UNIT_MAP.keys(),
         'value': 'Hertz'},
        {'name': 'Log scale', 'type': 'bool', 'value': True}
    ]},
    {'name': 'Y axis', 'type': 'group', 'children': [
        {'name': 'Format', 'type': 'list', 'values': YAXIS_FORMAT_MAP.keys(),
         'value': 'Linear magnitude'},
        {'name': 'Units', 'type': 'list', 'values': YAXIS_UNIT_MAP.keys(),
         'value': 'PSD (Volts^2/Hz)'},
        {'name': 'Unit amplitude', 'type': 'list', 'values': VOLT_MAP.keys(),
         'value': 'RMS'},
        {'name': 'Log scale', 'type': 'bool', 'value': False}
    ]}
]}

CHANNEL = ["Channel 1", "Channel 1 and Channel 2"]

INPUT_PARAM = {'name': 'Inputs', 'type': 'group', 'children': [
    {'name': 'Reject overload', 'type': 'bool', 'value': True},
    {'name': 'Channel 1', 'type': 'group', 'children': [
        {'name': 'Coupling', 'type': 'list',
         'values': INPUT_COUPLING, 'value': 'AC'},
        {'name': 'Impedance', 'type': 'list', 'values': INPUT_IMPEDANCE},
        {'name': 'Autorange', 'type': 'bool', 'value': False},
    ]},
    {'name': 'Channel 2', 'type': 'group', 'children': [
        {'name': 'Enable', 'type': 'bool', 'value': False},
        {'name': 'Coupling', 'type': 'list',
         'values': INPUT_COUPLING, 'value': 'AC'},
        {'name': 'Impedance', 'type': 'list', 'values': INPUT_IMPEDANCE},
        {'name': 'Autorange', 'type': 'bool', 'value': False},
    ]}
]}

SCALE_PARAM = {'name': 'Scaling data', 'type': 'group', 'children': [
    {'name': 'Multiplier', 'type': 'float', 'value': 1.0},
    {'name': 'Offset', 'type': 'float', 'value': 0.0},
    {'name': 'Reset', 'type': 'action'}
]}

SOURCE_PARAM = {'name': 'Source', 'type': 'group', 'children': [
    {'name': 'Enable', 'type': 'bool', 'value': False},
    {'name': 'Shape', 'type': 'list', 'values': SOURCE_SHAPE_MAP},
    {'name': 'Level', 'type': 'float', 'step': 0.1,
     'limits': SOURCE_LEVEL_VRMS_LIMITS, 'value': 0},
    {'name': 'Offset', 'type': 'float', 'step': 0.1,
     'limits': SOURCE_OFFSET_LIMITS, 'value': 0}
]}

TEXT_PARAM = {'name': 'Notes', 'type': 'text'}

ANALYZER_PARAM = [
    IO_PARAM,
    ACQ_PARAM,
    DISPLAY_PARAM,
    INPUT_PARAM,
    SCALE_PARAM,
    SOURCE_PARAM,
    TEXT_PARAM
]


# =============================================================================
class PreferenceDialog(QtWidgets.QDialog):
    """PreferenceDialog class, generates the ui of the preference form.
    """
    
    def __init__(self, ip="", port="", gpib_addr="", ccolor=QtGui.QColor(QtCore.Qt.black)):
        """Constructor.
        :param ip: IP of Prologix GPIB-Ethernet adapter (str)
        :param port: Port of Prologix GPIB-Ethernet adapter (int)
        :param gpib_addr: GPIB address of 34972A device (int)
        :param ccolor: the color of the curve (QColor)
        :returns: None
        """
        super().__init__()
        self.setWindowTitle("Preferences")
        # Lays out
        dev_gbox = QtWidgets.QGroupBox("FFT")
        self._ip_led = QtWidgets.QLineEdit(ip)
        self._ip_led.setInputMask("000.000.000.000;")
        self._port_led = QtWidgets.QLineEdit(port)
        self._port_led.setInputMask("0000;")
        self._gpib_addr_led = QtWidgets.QLineEdit(gpib_addr)
        self._gpib_addr_led.setInputMask("00;")
        self._check_interface_btn = QtWidgets.QPushButton("Check")
        self._check_interface_btn.setToolTip("Check connection with device")
        self._ccolor_btn = QtWidgets.QPushButton()
        self._ccolor_btn.setMaximumWidth(20)
        self._ccolor_btn.setAutoFillBackground(True)
        self.ccolor = ccolor
        dev_lay = QtWidgets.QGridLayout()
        dev_lay.addWidget(QtWidgets.QLabel("IP Prologix"), 0, 0)
        dev_lay.addWidget(self._ip_led, 0, 1)
        dev_lay.addWidget(QtWidgets.QLabel("Port Prologix"), 1, 0)
        dev_lay.addWidget(self._port_led, 1, 1)
        dev_lay.addWidget(QtWidgets.QLabel("GPIB address"), 2, 0)
        dev_lay.addWidget(self._gpib_addr_led, 2, 1)
        dev_lay.addWidget(self._check_interface_btn, 3, 0, 1, 0)
        dev_lay.addWidget(QtWidgets.QLabel("Curve color"), 4, 0)
        dev_lay.addWidget(self._ccolor_btn, 4, 1)
        dev_gbox.setLayout(dev_lay)
        self._btn_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok |
            QtWidgets.QDialogButtonBox.Cancel)
        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addWidget(dev_gbox)
        main_lay.addWidget(self._btn_box)
        self.setLayout(main_lay)
        # Logic
        self._btn_box.accepted.connect(self.accept)
        self._btn_box.rejected.connect(self.close)
        self._check_interface_btn.released.connect(self._check_interface)
        self._ccolor_btn.released.connect(self._choose_ccolor)

    @property
    def ip(self):
        """Getter of the IP value.
        :returns: IP value of device (str)
        """
        return self._ip_led.text()

    @property
    def port(self):
        """Getter of the TCP port value.
        :returns: TCP port value of device (int)
        """
        return int(self._port_led.text())

    @property
    def gpib_addr(self):
        """Getter of the GPIB address value.
        :returns: GPIB address of device (int)
        """
        return int(self._gpib_addr_led.text())

    @property
    def ccolor(self):
        """Gets the color property.
        :returns: the color of the curve (QColor)
        """
        return self._ccolor

    @ccolor.setter
    def ccolor(self, ccolor):
        """Set the color property.
        :param ccolor: the color of the curve (QColor)
        :returns: None
        """
        self._ccolor = ccolor
        if ccolor is None:
            return
        style = "background-color : {}; border: none;".format(ccolor.name())
        self._ccolor_btn.setStyleSheet(style)

    def _choose_ccolor(self):
        """Open a color dialog box and select a color for the curve.
        :returns: None
        """
        if self.ccolor is None:
            ccolor = QtGui.QColorDialog().getColor(parent=self,
                                                title="Select channel color")
        else:
            ccolor = QtGui.QColorDialog().getColor(self.ccolor, self,
                                                "Select channel color")
        if ccolor.isValid() is True:
            self.ccolor = ccolor

    def _check_interface(self):
        """To be subclassed.
        """
        pass


# =============================================================================
class FftPlot(pg.PlotWidget):
    """The Plot class is dedicated to display a graph.
    The class is derived from pyqtgraph.PlotWidget.
    """

    def __init__(self, parent=None, background='default', **kargs):
        """Constructor.
        """
        super().__init__(parent, background, **kargs)
        self.psd = None
        self.legend = None
        self._customize_plot()

    def _customize_plot(self):
        """Customize look of widget.
        :returns: None
        """
        self.setTitle('')  # Cosmetic: add space above plot
        self.setLabel('left', "")
        self.setLabel('bottom', "")
        self.setLogMode(x=True, y=False)
        self.enableAutoRange(pg.ViewBox.XYAxes, False)
        self.showGrid(x=True, y=True, alpha=0.8)

    def clear(self):
        """Clear plot.
        :returns: None
        """
        super().clear()
        self.psd = None
        self.legend = None

    def set_data(self, x=[], y=[], name="serie",
                 ccolor=QtGui.QColor(QtCore.Qt.black)):
        """Plot data on graph.
        :arg x: x-axis of plot (array)
        :arg y: y-axis of plot (array)
        :arg name: name of the curve (str)
        :arg ccolor: color of the curve (QColor)
        :returns: None
        """
        self.clear()
        self.enableAutoRange(pg.ViewBox.XYAxes, True)
        self.psd = self.plot(x, y, pen=pg.mkPen(ccolor), name=name)
        self.enableAutoRange(pg.ViewBox.XYAxes, False)

    def set_xlabel(self, label, units=None):
        self.setLabel('bottom', label, units=units)

    def set_ylabel(self, label, units=None):
        self.setLabel('left', label, units=units)


# =============================================================================
class FftWidget(QtWidgets.QWidget):
    """Widget dedicated to display the result of acquisition.
    """

    workspace_changed = QtCore.pyqtSignal(str)

    def __init__(self):
        """Initialization.
        """
        super().__init__()
        self.plot = FftPlot()
        self.params = Parameter.create(name='FFT parameters',
                                       type='group',
                                       children=ANALYZER_PARAM)
        self.param_tree = ParameterTree()
        self.param_tree.setParameters(self.params, showTop=False)
        self.param_tree.resizeColumnToContents(1)
        self.param_tree.resizeColumnToContents(2)
        self.param_tree.setMinimumSize(192, 192)
        splitter = QtWidgets.QSplitter(self)
        splitter.addWidget(self.param_tree)
        splitter.addWidget(self.plot)
        ui_layout = QtWidgets.QHBoxLayout()
        ui_layout.addWidget(splitter)
        self.setLayout(ui_layout)           
        #
        self.params.param('Acquisition', 'Start').sigValueChanged. \
            connect(self._start_changed)
        self.params.param('Acquisition', 'Stop').sigValueChanged. \
            connect(self._stop_changed)
        self.params.param('IO parameters', 'Choose workspace').sigActivated. \
            connect(self._workspace_dialog)
        self.workspace_changed.connect(
            self.params.param('IO parameters',
                              'Choose workspace',
                              'Working directory').setValue)
        self.workspace_changed.connect(
            lambda: self.param_tree.resizeColumnToContents(2))
        self.params.param('Display', 'X axis', 'Log scale').sigValueChanged. \
            connect(self._xscale_changed)
        self.params.param('Display', 'Y axis', 'Log scale').sigValueChanged. \
            connect(self._yscale_changed)

    def _start_changed(self):
        """Check that start and stop frequency value are consistents.
        """
        fstart = self.params.param('Acquisition', 'Start').value()
        fstop = self.params.param('Acquisition', 'Stop').value()
        if fstart in list(LOG_FREQ_START_MAP.keys()) and \
           fstop in list(LOG_FREQ_STOP_MAP.keys()):
            idx_start = list(LOG_FREQ_START_MAP.keys()).index(fstart)
            idx_stop = list(LOG_FREQ_STOP_MAP.keys()).index(fstop)
            if idx_start > idx_stop:
                self.params.param('Acquisition', 'Stop'). \
                    setValue(list(LOG_FREQ_STOP_MAP.keys())[idx_start])

    def _stop_changed(self):
        """Check that start and stop frequency value are consistents.
        """
        fstart = self.params.param('Acquisition', 'Start').value()
        fstop = self.params.param('Acquisition', 'Stop').value()
        if fstart in list(LOG_FREQ_START_MAP.keys()) and \
           fstop in list(LOG_FREQ_STOP_MAP.keys()):
            idx_start = list(LOG_FREQ_START_MAP.keys()).index(fstart)
            idx_stop = list(LOG_FREQ_STOP_MAP.keys()).index(fstop)
            if idx_start > idx_stop:
                self.params.param('Acquisition', 'Start'). \
                    setValue(list(LOG_FREQ_START_MAP.keys())[idx_stop])

    def _workspace_dialog(self):
        """Choose path to workspace. Call a file dialog box to choose
        the working directory.
        :returns: choosen directory else an empty string (str)
        """
        workspace_dir = QtWidgets.QFileDialog().getExistingDirectory(
            parent=None,
            caption="Choose workspace directory",
            directory=path.expanduser("~"))
        if workspace_dir == "":
            return ""
        self.workspace_changed.emit(workspace_dir)
        return workspace_dir

    def _xscale_changed(self):
        """Handle display of X axis scale.
        """
        xscale = self.params.param('Display', 'X axis', 'Log scale').value()
        self.plot.setLogMode(x=xscale)

    def _yscale_changed(self):
        """Handle display of Y axis scale.
        """
        
        yscale = self.params.param('Display', 'Y axis', 'Log scale').value()
        self.plot.setLogMode(y=yscale)


# =============================================================================
class MainWindow(QtWidgets.QMainWindow):
    """MainWindow class, main UI of FFT program.
    """

    file_droped = QtCore.pyqtSignal(str)
    workspace_changed = QtCore.pyqtSignal(str)

    def __init__(self):
        """Constructor.
        """
        super().__init__()
        self.setWindowTitle(APP_NAME)
        # Lays out
        self._create_actions()
        self._menu_bar = self.menuBar()
        self._populate_menubar()
        self.tool_bar = self.addToolBar("Tool Bar")
        self._populate_toolbar()
        self.tool_bar.setMovable(True)
        self.tool_bar.setFloatable(False)
        self.status_bar = self.statusBar()
        self.data_tab = QtWidgets.QTabWidget()
        self.data_tab.addTab(FftWidget(), "New")
        self.setCentralWidget(self.data_tab)
        #
        self._state = self.data_tab.currentWidget().params.saveState()
        #
        self.current_tab.workspace_changed.connect(self.workspace_changed.emit)
        self.setAcceptDrops(True)
        #
        self.action_copy_param.triggered.connect(self._copy_parameter)
        self.action_paste_param.triggered.connect(self._paste_parameter)
        #
        self.data_tab.currentWidget().param_tree.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu)
        self.data_tab.currentWidget().param_tree.customContextMenuRequested. \
            connect(self.open_context_menu)
        # Init widget display
        self.reset()

    def _create_actions(self):
        """Creates actions used with bar widgets.
        :returns: None
        """
        #
        self.action_new = QtWidgets.QAction(
            QtGui.QIcon.fromTheme("document-new"), "&New", self)
        self.action_new.setStatusTip("New data form")
        self.action_new.setShortcut('Ctrl+N')
        #
        self.action_run = QtWidgets.QAction(
            QtGui.QIcon.fromTheme("system-run"), "&Run", self)
        self.action_run.setStatusTip("Run acquisition")
        self.action_run.setShortcut('Ctrl+N')
        #
        self.action_get_screen = QtWidgets.QAction(
            QtGui.QIcon.fromTheme("system-run"), "&Get screen", self)
        self.action_get_screen.setStatusTip("Get screen display")
        #
        self.action_cancel = QtWidgets.QAction(
            QtGui.QIcon.fromTheme("process-stop"), "&Cancel", self)
        self.action_cancel.setStatusTip("Cancel acquisition")
        self.action_cancel.setShortcut('Ctrl+D')
        #
        self.action_save_as = QtWidgets.QAction(
            QtGui.QIcon.fromTheme("document-save"), ("Save &As"), self)
        self.action_save_as.setStatusTip("Save data as")
        self.action_save_as.setShortcut('Ctrl+A')
        #
        self.action_reset_dev = QtWidgets.QAction(
            QtGui.QIcon.fromTheme("system-reboot"), "&Reset device", self)
        self.action_reset_dev.setStatusTip("Reset device")
        #
        self.action_quit = QtWidgets.QAction(
            QtGui.QIcon.fromTheme("application-exit"), "&Quit", self)
        self.action_quit.setStatusTip("Exit application")
        self.action_quit.setShortcut('Ctrl+Q')
        #
        self.action_pref = QtWidgets.QAction(
            QtGui.QIcon.fromTheme("preferences-system"),
            "Preferences", self)
        self.action_pref.setStatusTip("Open preference dialog form")
        #
        self.action_copy_param = QtWidgets.QAction(
            QtGui.QIcon.fromTheme("edit-copy"), "&Copy parameters", self)
        self.action_copy_param.setShortcut('Ctrl+C')
        #
        self.action_paste_param = QtWidgets.QAction(
            QtGui.QIcon.fromTheme("edit-paste"), "Paste parameters", self)
        self.action_paste_param.setShortcut('Ctrl+V')
        #
        self.action_about = QtWidgets.QAction(
            QtGui.QIcon.fromTheme("help-about"),
            "About {}".format(APP_NAME), self)
        self.action_about.setStatusTip("Open about dialog form")

    def _populate_menubar(self):
        """Populates the menubar of the UI
        :returns: None
        """
        self._menu_bar.menu_file = self._menu_bar.addMenu("&File")
        self._menu_bar.menu_file.addAction(self.action_new)
        self._menu_bar.menu_file.addAction(self.action_save_as)
        self._menu_bar.menu_file.addSeparator()
        self._menu_bar.menu_file.addAction(self.action_pref)
        self._menu_bar.menu_file.addAction(self.action_quit)
        self._menu_bar.menu_process = self._menu_bar.addMenu("&Process")
        self._menu_bar.menu_process.addAction(self.action_run)
        self._menu_bar.menu_process.addAction(self.action_cancel)
        self._menu_bar.menu_process.addAction(self.action_get_screen)
        self._menu_bar.menu_process.addAction(self.action_reset_dev)
        self._menu_bar.menu_help = self._menu_bar.addMenu("&Help")
        self._menu_bar.menu_help.addAction(self.action_about)

    def _populate_toolbar(self):
        """Populates the toolbar of the UI.
        :returns: None
        """
        self.tool_bar.addAction(self.action_run)
        self.tool_bar.addAction(self.action_cancel)
        self.tool_bar.addAction(self.action_new)

    @QtCore.pyqtSlot()
    def reset(self):
        """Reset UI. This is the starting state when no data file is imported,
        functions regarding data processing are not accessible.
        :returns: None
        """
        self.action_run.setEnabled(True)
        self.action_save_as.setEnabled(False)
        self.action_new.setEnabled(True)
        self.action_cancel.setEnabled(False)

    @property
    def current_tab_text(self):
        return self.data_tab.tabText()

    @current_tab_text.setter
    def current_tab_text(self, text):
        self.data_tab.setTabText(self.data_tab.currentIndex(), text)

    @property
    def current_tab(self):
        return self.data_tab.currentWidget()

    @QtCore.pyqtSlot(str)
    def acquisition_state(self, mode='done'):
        """Set UI in acquisition state. Some action need to be enable/disable
        during acquisition process.
        :returns: None
        """
        if mode == 'ini':
            self.action_run.setEnabled(True)
            self.action_save_as.setEnabled(False)
            self.action_cancel.setEnabled(False)
            self.action_new.setEnabled(False)
        elif mode == 'running':
            self.action_run.setEnabled(False)
            self.action_save_as.setEnabled(False)
            self.action_cancel.setEnabled(True)
            self.action_new.setEnabled(False)
        else:  # 'done'
            self.action_run.setEnabled(True)
            self.action_save_as.setEnabled(True)
            self.action_cancel.setEnabled(False)
            self.action_new.setEnabled(True)

    def set_filename(self, value):
        self.current_tab.params.param('Temporal analysis', 'Filename'). \
            setValue(ntpath.basename(value))
        self.data_tab.setTabText(self.data_tab.currentIndex(), value)

    def open_context_menu(self, position):
        menu = QtWidgets.QMenu(self)
        copy_action = menu.addAction("Copy")
        paste_action = menu.addAction("Paste")
        action = menu.exec_(
            self.data_tab.currentWidget().param_tree.mapToGlobal(position))
        if action == paste_action:
            self._paste_parameter()
        elif action == copy_action:
            self._copy_parameter()

    def _paste_parameter(self):
        self.data_tab.currentWidget().params.restoreState(self._state)

    def _copy_parameter(self):
        self._state = self.data_tab.currentWidget().params.saveState()

    # The following three methods set up dragging and dropping for the app
    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls:
            e.accept()
        else:
            e.ignore()

    def dragMoveEvent(self, e):
        if e.mimeData().hasUrls:
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        """Drop files directly onto the widget.
        File locations are stored in fname.
        :param e:
        :return:
        """
        if e.mimeData().hasUrls:
            e.setDropAction(QtCore.Qt.CopyAction)
            e.accept()
            # Workaround for OSx dragging and dropping
            for url in e.mimeData().urls():
                fname = str(url.toLocalFile())
            self.file_droped.emit(fname)
        else:
            e.ignore()


# =============================================================================
if __name__ == "__main__":

    import sys
    import numpy as np

    # Handles log
    DATE_FMT = "%d/%m/%Y %H:%M:%S"
    LOG_FORMAT = "%(asctime)s %(levelname) -8s %(filename)s " + \
                 " %(funcName)s (%(lineno)d): %(message)s"
    logging.basicConfig(level=logging.DEBUG,
                        datefmt=DATE_FMT,
                        format=LOG_FORMAT)

    def scale_data(ui, m_factor, o_factor):
        ditem = ui.current_tab.plot.plotItem.dataItems
        for c in ditem:
            y = c.yData * m_factor + o_factor
            ui.current_tab.plot.set_data(x=c.xData, y=y)

    def preference(ui):
        dialog = PreferenceDialog()
        dialog.setParent(ui, QtCore.Qt.Dialog)
        retval = dialog.exec_()
            
    X = np.arange(1, 10)
    Y = np.arange(1, 10)**2

    APP = QtWidgets.QApplication(sys.argv)

    UI = MainWindow()
    UI.current_tab.plot.set_data(x=X, y=Y)
    UI.action_pref.triggered.connect(lambda: preference(UI))

    UI.show()

    scale_data(UI, 10, -10)

    sys.exit(APP.exec_())
