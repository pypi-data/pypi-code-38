# -*- coding: utf-8 -*-

"""package fft_dev
author  Benoit Dubois
copyright FEMTO ENGINEERING, 2019
license GPL v3.0+
brief   UI to handle the HP3562A FFT device.
"""

from PyQt5 import QtCore, QtWidgets, QtGui
import pyqtgraph as pg


# =============================================================================
class PreferenceDialog(QtWidgets.QDialog):
    """PreferenceDialog class, generates the ui of the preference form.
    """

    def __init__(self, ip="", port=None, gpib_addr=None):
        """Constructor.
        :param ip: IP of Prologix GPIB-Ethernet adapter (str)
        :param port: Port of Prologix GPIB-Ethernet adapter (int)
        :param gpib_addr: GPIB address of 34972A device (int)
        :returns: None
        """
        super().__init__()
        self.setWindowTitle("Preferences")
        # Lays out
        dev_gbox = QtWidgets.QGroupBox("HP3562A")
        self.ip_led = QtWidgets.QLineEdit(ip)
        self.ip_led.setInputMask("000.000.000.000;")
        self.port_led = QtWidgets.QLineEdit(port)
        self.port_led.setInputMask("0000;")
        self.gpib_addr_led = QtWidgets.QLineEdit(gpib_addr)
        self.gpib_addr_led.setInputMask("00;")
        self._check_interface_btn = QtWidgets.QPushButton("Check")
        self._check_interface_btn.setToolTip("Check connection with device")
        dev_lay = QtWidgets.QGridLayout()
        dev_lay.addWidget(QtWidgets.QLabel("IP Prologix"), 0, 0)
        dev_lay.addWidget(self.ip_led, 0, 1)
        dev_lay.addWidget(QtWidgets.QLabel("Port Prologix"), 1, 0)
        dev_lay.addWidget(self.port_led, 1, 1)
        dev_lay.addWidget(QtWidgets.QLabel("GPIB address"), 2, 0)
        dev_lay.addWidget(self.gpib_addr_led, 2, 1)
        dev_lay.addWidget(self._check_interface_btn, 3, 0, 1, 0)
        dev_gbox.setLayout(dev_lay)
        self._btn_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addWidget(dev_gbox)
        main_lay.addWidget(self._btn_box)
        self.setLayout(main_lay)
        # Logic
        self._btn_box.accepted.connect(self.accept)
        self._btn_box.rejected.connect(self.close)
        self._check_interface_btn.released.connect(self._check_interface)

    def _check_interface(self):
        """Must be implemented in derived class
        """
        pass

    @property
    def ip(self):
        """Getter of the IP value.
        :returns: IP value of device (str)
        """
        return self.ip_led.text()

    @property
    def port(self):
        """Getter of the TCP port value.
        :returns: TCP port value of device (int)
        """
        return self.port_led.text()

    @property
    def gpib_addr(self):
        """Getter of the GPIB address value.
        :returns: GPIB address of device (int)
        """
        return self.gpib_addr_led.text()


# =============================================================================
class Fft3562aMainWindow(QtWidgets.QMainWindow):
    """Fft3562aMainWindow class, main UI of fft3562a-gui.
    """

    workspace_changed = QtCore.pyqtSignal(str)

    def __init__(self):
        """Constructor.
        :returns: None
        """
        super().__init__()
        # Lays out
        self._create_actions()
        self._menu_bar = self.menuBar()
        self._populate_menubar()
        self.tool_bar = self.addToolBar("Tool Bar")
        self._populate_toolbar()
        self.tool_bar.setMovable(True)
        self.tool_bar.setFloatable(False)
        self.tool_bar.setAllowedAreas(QtCore.Qt.AllToolBarAreas)
        self.status_bar = self.statusBar()
        central_widget = self._central_widget()
        self.setCentralWidget(central_widget)
        # UI handling
        self._ui_handling()

    def _central_widget(self):
        """Generates central widget.
        :returns: central widget of UI (QWidget)
        """
        self.gain_lbl = QtWidgets.QLabel("Gain (dB)")
        self.gain_dsb = QtWidgets.QDoubleSpinBox()
        self.gain_dsb.setRange(-999, 999)
        self.sensitivity_lbl = QtWidgets.QLabel("Sensitivity (rad/V)")
        self.sensitivity_dsb = QtWidgets.QDoubleSpinBox()
        self.sensitivity_dsb.setRange(-999, 999)
        self.workspace_btn = QtWidgets.QToolButton()
        self.workspace_btn.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.workspace_lbl = QtWidgets.QLabel()
        setup_lay = QtWidgets.QHBoxLayout()
        setup_lay.addWidget(self.gain_lbl)
        setup_lay.addWidget(self.gain_dsb)
        setup_lay.addSpacing(10)
        setup_lay.addWidget(self.sensitivity_lbl)
        setup_lay.addWidget(self.sensitivity_dsb)
        setup_lay.addSpacing(10)
        setup_lay.addWidget(self.workspace_btn)
        setup_lay.addSpacing(5)
        setup_lay.addWidget(self.workspace_lbl)
        setup_lay.setStretchFactor(self.gain_dsb, 2)
        setup_lay.setStretchFactor(self.sensitivity_dsb, 2)
        setup_lay.setStretchFactor(self.workspace_lbl, 1)
        #
        self.mplot = pg.GraphicsView()
        #
        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addLayout(setup_lay)
        main_lay.addWidget(self.mplot)
        main_lay.setStretchFactor(self.mplot, 2)
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(main_lay)
        return central_widget

    def _populate_menubar(self):
        """Populates the menu bar of the UI
        :returns: None
        """
        self._menu_bar.menu_file = self._menu_bar.addMenu("&File")
        # self._menu_bar.menu_file.addAction(self.action_save)
        # self._menu_bar.menu_file.addSeparator()
        self._menu_bar.menu_file.addAction(self.action_quit)
        self._menu_bar.menu_edit = self._menu_bar.addMenu("&Edit")
        self._menu_bar.menu_edit.addAction(self.action_pref)
        self._menu_bar.menu_process = self._menu_bar.addMenu("&Process")
        self._menu_bar.menu_process.addAction(self.action_acq)
        self._menu_bar.menu_help = self._menu_bar.addMenu("&Help")
        self._menu_bar.menu_help.addAction(self.action_about)

    def _populate_toolbar(self):
        """Populates the tool bar of the UI
        :returns: None
        """
        self.tool_bar.addAction(self.action_acq)
        # self.tool_bar.addAction(self.action_save)

    def _create_actions(self):
        """Creates actions used with bar widgets.
        :returns: None
        """
        # self.action_save = QAction(QIcon.fromTheme("document-save"),
        #                           "&Save", self)
        # self.action_save.setStatusTip("Save data")
        # self.action_save.setShortcut('Ctrl+S')"""
        #
        self.action_quit = QtWidgets.QAction(
            QtGui.QIcon.fromTheme("application-exit"),
            "&Quit", self)
        self.action_quit.setStatusTip("Exit application")
        self.action_quit.setShortcut('Ctrl+Q')
        #
        self.action_acq = QtWidgets.QAction(
            QtGui.QIcon.fromTheme("system-run"),
            "&Acquisition", self)
        self.action_acq.setStatusTip("Run acquisition")
        self.action_acq.setShortcut('Ctrl+A')
        #
        self.action_workspace = QtWidgets.QAction(
            QtGui.QIcon.fromTheme("folder-new"),
            "Choose &workspace", self)
        self.action_workspace.setStatusTip("Choose workspace directory")
        self.action_workspace.setShortcut('Ctrl+W')
        #
        self.action_pref = QtWidgets.QAction(
            QtGui.QIcon.fromTheme("preferences-system"),
            "P&references", self)
        self.action_pref.setStatusTip("Open preference dialog form")
        self.action_pref.setShortcut('Ctrl+R')
        #
        self.action_about = QtWidgets.QAction(
            QtGui.QIcon.fromTheme("help-about"),
            "A&bout fft3562a", self)
        self.action_about.setStatusTip("Open about dialog form")
        self.action_about.setShortcut('Ctrl+B')

    def _ui_handling(self):
        """Basic (local) ui handling.
        :returns: None
        """
        self.workspace_btn.setDefaultAction(self.action_workspace)
        self.action_workspace.triggered.connect(self._workspace_dialog)
        self.workspace_changed.connect(self.workspace_lbl.setText)

    @QtCore.pyqtSlot()
    def _workspace_dialog(self):
        """Choose path to workspace. Call a file dialog box to choose
        the working directory.
        :returns: choosen directory else an empty string (str)
        """
        workspace_dir = QtWidgets.QFileDialog().getExistingDirectory(
            parent=None,
            caption="Choose workspace directory",
            directory=QtCore.QDir.currentPath())
        if workspace_dir == "":
            return ""
        self.workspace_changed.emit(workspace_dir)
        return workspace_dir


# =============================================================================
def display_ui():
    """Displays the main UI.
    """
    import sys

    app = QtWidgets.QApplication(sys.argv)
    ui = Fft3562aMainWindow()
    ui.show()
    sys.exit(app.exec_())


# =============================================================================
if __name__ == "__main__":
    display_ui()
