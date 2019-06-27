# -*- coding: utf-8 -*-

"""package dmm
author  Benoit Dubois
version 0.1
license GPL v3.0+
date    2014-25-03
brief   UI to handle the 34972A data logger application.
"""

from PyQt4 import Qt
from PyQt4.QtCore import pyqtSignal, pyqtSlot, QSignalMapper, QEvent
from PyQt4.QtGui import QApplication, QMainWindow, QWidget, QLabel, QAction, \
     QComboBox, QIcon, QVBoxLayout, QCheckBox, QTabWidget, QDialog, QGroupBox, \
     QLineEdit, QDialogButtonBox, QScrollArea, QPushButton

from widgetben import FlowLayout
from widgetben import EPlotWidget

from _34972a_dev import Dev34972aWorker
from dev.constants import DEF_PORT, DEVICE_ID, APP_NAME


#===============================================================================
# Class MyQCheckBox
#===============================================================================
class MyQComboBox(QComboBox):
    """MyQCheckBox class, add generation of enabled change signals.
    """

    enabled_changed = pyqtSignal(bool)

    def __init__(self, *args, **kwargs):
        """Constructor.
        :returns: None
        """
        super(MyQComboBox, self).__init__(*args, **kwargs)

    def changeEvent(self, event):
        """Overloaded method.
        :param event: intercepted event (QEvent)
        :returns: None
        """
        super(MyQComboBox, self).changeEvent(event)
        if event == QEvent.EnabledChange:
            self.enabled_changed.emit(self.isEnabled)


#===============================================================================
# Class PreferenceDialog
#===============================================================================
class PreferenceDialog(QDialog):
    """PreferenceDialog class, generates the ui of the preference form.
    """

    def __init__(self, dev=None, ip="", mjd=False, parent=None):
        """Constructor.
        :param dev: device class instance (object)
        :param ip: IP of 34972A device (str)
        :param mjd: Modified Julian Day flag (bool)
        :param ip: parent object (object)
        :returns: None
        """
        if dev not in DEVICE.values():
            raise KeyError("Device not handled by GUI") 
        super(PreferenceDialog, self).__init__(parent)

        self.setWindowTitle(self.trUtf8("Preferences"))
        # Lays out
        dev_gbox = QGroupBox(self.trUtf8("Interface"))
        self.ip_led = QLineEdit(ip)
        self.ip_led.setInputMask("000.000.000.000;")
        self._check_interface_btn = QPushButton(self.trUtf8("Check"))
        self._check_interface_btn.setToolTip(
            self.trUtf8("Check connection with device"))
        dev_lay = QVBoxLayout()
        dev_lay.addWidget(QLabel(self.trUtf8("IP")))
        dev_lay.addWidget(self.ip_led)
        dev_lay.addWidget(self._check_interface_btn)
        dev_gbox.setLayout(dev_lay)
        file_gbox = QGroupBox(self.trUtf8("Data file"))
        self.mjd_ckbox = QCheckBox()
        if mjd == True:
            self.mjd_ckbox.setCheckState(Qt.Qt.Checked)
        else:
            self.mjd_ckbox.setCheckState(Qt.Qt.Unchecked)
        file_lay = QVBoxLayout()
        file_lay.addWidget(QLabel("Use Modified Julian Day"))
        file_lay.addWidget(self.mjd_ckbox)
        file_gbox.setLayout(file_lay)
        self._btn_box = QDialogButtonBox(QDialogButtonBox.Ok | \
                                         QDialogButtonBox.Cancel)
        main_lay = QVBoxLayout()
        main_lay.addWidget(dev_gbox)
        main_lay.addWidget(file_gbox)
        main_lay.addWidget(self._btn_box)
        self.setLayout(main_lay)
        # Basic logic
        self._btn_box.accepted.connect(self.accept)
        self._btn_box.rejected.connect(self.close)
        self._check_interface_btn.released.connect(dev.check_interface)
        dev.id_checked.connect(self._check_interface)

    @pyqtSlot(bool)
    def _check_interface(self, is_ok):
        """Returns True if interface with device is OK.
        :param is_ok: if True, connection on interface is OK else False (bool)
        :returns: status of interface with device (boolean)
        """
        if is_ok is True:
            self._check_interface_btn.setStyleSheet( \
                "QPushButton { background-color : green; color : yellow; }")
            self._check_interface_btn.setText("OK")
        else:
            self._check_interface_btn.setStyleSheet( \
                "QPushButton { background-color : red; color : blue; }")
            self._check_interface_btn.setText("Error")

    @property
    def ip(self):
        """Getter of the IP value.
        :returns: IP of device (str)
        """
        return self.ip_led.text()

    @property
    def mjd(self):
        """Getter of the mjd parameter selection.
        :returns: MJD state (bool)
        """
        if self.mjd_ckbox.checkState() == Qt.Qt.Checked:
            return True
        else:
            return False


#===============================================================================
# CLASS ParamWdgt
#===============================================================================
class ParamWdgt(QWidget):
    """ParamWdgt class, used to handle the graphical configuration of a
    channel of the 34901 module.
    """

    range_changed = pyqtSignal(int)
    reso_changed = pyqtSignal(int)

    def __init__(self, func_list):
        """Constructor: setup ui.
        :param func_list: list of measurement functions supported by channel
        (list of str)
        :retuns: None
        """
        super(ParamWdgt, self).__init__()
        self.func_cbox = QComboBox()
        self.rang_cbox = QComboBox()
        self.reso_cbox = QComboBox()
        self.intgt_cbox = QComboBox()
        # Lays out
        layout = QVBoxLayout()
        layout.addWidget(self.func_cbox)
        layout.addWidget(self.rang_cbox)
        layout.addWidget(self.reso_cbox)
        layout.addWidget(self.intgt_cbox)
        self.setLayout(layout)
        # Generates signals
        self.reso_cbox.currentIndexChanged.connect(self.reso_changed.emit)
        self.rang_cbox.currentIndexChanged.connect(self.range_changed.emit)
        # UI handling
        self._ui_handling()
        # Inits widgets
        for reso in Dev.RESO:
            self.reso_cbox.addItem(self.trUtf8(reso.caption))
        for intgt in Dev.INTGT:
            self.intgt_cbox.addItem(self.trUtf8(intgt.caption))
        for func in func_list:
            self.func_cbox.addItem(self.trUtf8(func))

    def _ui_handling(self):
        """Basic ui handling. Handles widget enabling/disabling.
        Resolution and integration time value are linked.
        :returns: None
        """
        self.func_cbox.currentIndexChanged.connect(self.set_range_list)
        self.reso_cbox.currentIndexChanged.connect( \
            self.intgt_cbox.setCurrentIndex)
        self.intgt_cbox.currentIndexChanged.connect( \
            self.reso_cbox.setCurrentIndex)
        self.rang_cbox.currentIndexChanged.connect(self._range_handling)

    @pyqtSlot(int)
    def _range_handling(self):
        """Specific range parameter handling.
        Resolution value needs to be disabled if range is set to AUTO mode.
        :returns: None
        """
        if self.rang_cbox.isEnabled() is True:
            if self.rang_cbox.currentIndex() == 0:
                self.reso_cbox.setCurrentIndex(0)
                self.reso_cbox.setDisabled(True)
                self.intgt_cbox.setCurrentIndex(0)
                self.intgt_cbox.setDisabled(True)
            else:
                self.reso_cbox.setEnabled(True)
                self.intgt_cbox.setEnabled(True)
        else:
            self.reso_cbox.setDisabled(True)
            self.intgt_cbox.setDisabled(True)

    def reset(self):
        """Resets the widget.
        :returns: None
        """
        self.func_cbox.setCurrentIndex(0)
        self.rang_cbox.setCurrentIndex(0)
        self.reso_cbox.setCurrentIndex(2)

    @property
    def func(self):
        """Getter for function property.
        :returns: index representing the selected function (int)
        """
        return self.func_cbox.currentIndex()

    @property
    def rang(self):
        """Getter for range property.
        :returns: index representing the selected range (int)
        """
        return self.rang_cbox.currentIndex()

    @property
    def reso(self):
        """Getter for resolution property.
        :returns: index representing the selected resolution (int)
        """
        return self.reso_cbox.currentIndex()

    @property
    def intgt(self):
        """Getter for integration time property.
        :returns: index representing the selected integration time (int)
        """
        return self.intgt_cbox.currentIndex()

    def set_func(self, value):
        """Setter for function property.
        :param value: index representing the selected function (int)
        :returns: None
        """
        self.func_cbox.setCurrentIndex(value)

    def set_rang(self, value):
        """Setter for range property.
        :param value: index representing the selected range (int)
        :returns: None
        """
        self.rang_cbox.setCurrentIndex(value)

    def set_reso(self, value):
        """Setter for resolution property.
        :param value: index representing the selected resolution (int)
        :returns: None
        """
        self.reso_cbox.setCurrentIndex(value)

    def set_intgt(self, value):
        """Setter for integration time property.
        :param value: index representing the selected integration time (int)
        :returns: None
        """
        self.intgt_cbox.setCurrentIndex(value)

    @pyqtSlot(int)
    def set_range_list(self, func_id):
        """Sets a new item list in the range combobox in respect with function
        sets in function combobox widget.
        :param func_id: current function identifier (int)
        :returns: None
        """
        self.rang_cbox.clear()
        range_list = Dev.FUNCTION_FULL[func_id].list
        for item in range_list:
            self.rang_cbox.addItem(self.trUtf8(item.caption))


#===============================================================================
# CLASS ChannelWdgt
#===============================================================================
class ChannelWdgt(QWidget):
    """ChannelWdgt class, used to handle the graphical configuration of a
    channel of the 34901 module.
    """

    state_changed = pyqtSignal(int)
    range_changed = pyqtSignal(int)
    reso_changed = pyqtSignal(int)

    def __init__(self, id_num, func_list):
        """Constructor: setup ui.
        :parma id_num: unique identification number (int)
        :param func_list: list of measurement functions supported by channel
        (list of str)
        :retuns: None
        """
        super(ChannelWdgt, self).__init__()
        self.id = id_num
        self.en_ckbox = QCheckBox(self.trUtf8("Enabled"))
        self.label = QLabel(self.trUtf8("Channel " + str(id_num)))
        self.param_wdgt = ParamWdgt(func_list)
        # Lays out
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.en_ckbox)
        layout.addWidget(self.param_wdgt)
        self.setLayout(layout)
        # Generates signals
        self.param_wdgt.range_changed.connect(self.range_changed.emit)
        self.param_wdgt.reso_changed.connect(self.reso_changed.emit)
        self.en_ckbox.stateChanged.connect(self.state_changed.emit)
        # UI handling
        self._ui_handling()
        # Inits widget
        self.reset()

    def _ui_handling(self):
        """Basic ui handling. Handles widget enabling/disabling.
        :returns: None
        """
        self.en_ckbox.stateChanged.connect(self.handle_state_change)

    def reset(self):
        """Resets the widget.
        :returns: None
        """
        self.param_wdgt.reset()
        self.setState(Qt.Qt.Unchecked)
        self.setEnabled(False)

    @property
    def func(self):
        """Getter for function property.
        :returns: index representing the selected function (int)
        """
        return self.param_wdgt.func

    @property
    def rang(self):
        """Getter for range property.
        :returns: index representing the selected range (int)
        """
        return self.param_wdgt.rang

    @property
    def reso(self):
        """Getter for resolution property.
        :returns: index representing the selected resolution (int)
        """
        return self.param_wdgt.reso

    @property
    def intgt(self):
        """Getter for integration time property.
        :returns: index representing the selected integration time (int)
        """
        return self.param_wdgt.intgt

    def set_func(self, value):
        """Setter for function property.
        :param value: index representing the selected function (int)
        :returns: None
        """
        self.param_wdgt.set_func(value)

    def set_rang(self, value):
        """Setter for range property.
        :param value: index representing the selected range (int)
        :returns: None
        """
        self.param_wdgt.set_rang(value)

    def set_reso(self, value):
        """Setter for resolution property.
        :param value: index representing the selected resolution (int)
        :returns: None
        """
        self.param_wdgt.set_reso(value)

    def set_intgt(self, value):
        """Setter for integration time property.
        :param value: index representing the selected integration time (int)
        :returns: None
        """
        self.parma_wdgt.set_intgt(value)

    def checkState(self):
        """Redefines method: returns the state of widget ie the state of the
        en_ckbox widget instead of the state of the widget itself, because
        the en_ckbox widget master the state of the widget.
        :returns: the state of the check box (int)
        """
        return self.en_ckbox.checkState()

    def setState(self, state):
        """Sets state property. See checkState().
        :param state: the state of the check box (int)
        """
        self.en_ckbox.setCheckState(state)

    def isEnabled(self):
        """Redefines method: returns the state of widget ie the state of the
        en_ckbox widget instead of the state of the widget itself, because
        the en_ckbox widget master the state of the widget.
        :returns: State of widget (bool)
        """
        return self.en_ckbox.isEnabled()

    def setEnabled(self, flag=True):
        """Redefines method: enables/disables whole widgets except en_ckbox
        widget, because the en_ckbox called this function.
        :param flag: new flag (bool)
        :returns: None
        """
        self.param_wdgt.setEnabled(flag)

    def handle_state_change(self, state):
        """Handles widget in respect with QCheckBox state.
        :param state: new state (int)
        :returns: None
        """
        self.setEnabled(True if state == Qt.Qt.Checked else False)


#===============================================================================
# CLASS Mod34901Wdgt
#===============================================================================
class Mod34901Wdgt(QWidget):
    """W34901Wdgt class, used to handle the graphical configuration of the
    34901 module.
    """

    channel_state_changed = pyqtSignal(int)
    channel_range_changed = pyqtSignal(int)
    channel_reso_changed = pyqtSignal(int)

    def __init__(self, slot=None):
        """Constructor.
        :param slot: slot number, between 1 to 3 (int)
        :returns: None
        """
        super(Mod34901Wdgt, self).__init__()
        self._slot = slot
        self._channels = {}
        for id_key in range(100*slot+1, 100*slot+21):
            self._channels[id_key] = ChannelWdgt(id_key, \
                            [idx.caption for idx in Dev.FUNCTION])
        for id_key in range(100*slot+21, 100*slot+23):
            self._channels[id_key] = ChannelWdgt(id_key, \
                            [idx.caption for idx in Dev.FUNCTION_FULL])
        # Layout
        scroll_layout = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll_layout.addWidget(scroll)
        scroll_wdgt = QWidget(self)
        dyn_layout = FlowLayout(scroll_wdgt)
        for channel in self._channels.itervalues():
            dyn_layout.addWidget(channel)
        scroll.setWidget(scroll_wdgt)
        scroll.setWidgetResizable(True)
        # Channel 21 and 22 are mutualy exclusives
        self._channels[100*slot+21].en_ckbox.stateChanged.connect( \
            lambda: self._exclu_chan(100*slot+21, [100*slot+21, 100*slot+22]))
        self._channels[100*slot+22].en_ckbox.stateChanged.connect( \
            lambda: self._exclu_chan(100*slot+20, [100*slot+21, 100*slot+22]))
        # Generates signals when a channel changes
        ## channel_state_changed()
        state_signal_mapper = QSignalMapper(self)
        for key, channel in self._channels.iteritems():
            state_signal_mapper.setMapping(channel, key)
            channel.state_changed.connect(state_signal_mapper.map)
        state_signal_mapper.mapped.connect(self.channel_state_changed)
        ## channel_range_changed()
        range_signal_mapper = QSignalMapper(self)
        for key, channel in self._channels.iteritems():
            range_signal_mapper.setMapping(channel, key)
            channel.range_changed.connect(range_signal_mapper.map)
        range_signal_mapper.mapped.connect(self.channel_state_changed)
        ## channel_reso_changed()
        reso_signal_mapper = QSignalMapper(self)
        for key, channel in self._channels.iteritems():
            reso_signal_mapper.setMapping(channel, key)
            channel.reso_changed.connect(reso_signal_mapper.map)
        reso_signal_mapper.mapped.connect(self.channel_state_changed)

    def __iter__(self):
        """Iterator: iterates over channels dict.
        """
        return iter(self._channels)

    def itervalues(self):
        """Iterator: iterates over channels dict.
        """
        return iter(self._channels.itervalues())

    def enabled_channels(self):
        """Getter of the list of enabled channel object (list).
        :returns: the list of enabled channel object (list)
        """
        en_list = []
        for channel in self._channels.itervalues():
            if channel.en_ckbox.checkState() == Qt.Qt.Checked:
                en_list.append(channel)
        return en_list

    def reset(self):
        """Resets UI.
        :returns: None
        """
        for channel in self._channels.itervalues():
            channel.reset()

    @property
    def slot(self):
        """Getter of the slot number.
        :returns: the dictionnary of channel object (dict)
        """
        return self._slot

    @property
    def channels(self):
        """Getter of the dictionnary of channel object (dict).
        :returns: the dictionnary of channel object (dict)
        """
        return self._channels

    def channel(self, id_key):
        """Getter of channel widget object (ChannelWdgt).
        :param id_key: key index of channel in the dict channel (str)
        :returns: a channel widget object (ChannelWdgt)
        """
        return self._channels[id_key]

    def _exclu_chan(self, channel_id, channel_id_list):
        """Handles mutual exclusif access of channel 20 and 21 (the only
        channels with capabilities of current measurement) ie ensures that
        only one channel is checked (notes that neither of the channels can
        been checked). Checks that 'channel' is the master over others channels.
        If this channel is checked, the others are unchecked.
        :param channel_id: the id number of the current master channel (int)
        :param channel_id_list: list of id of mutual exclusif channels (list)
        :returns: None
        """
        if self._channels[channel_id].en_ckbox.checkState() == Qt.Qt.Checked:
            channel_id_list.remove(channel_id)
            for ch in channel_id_list:
                self._channels[ch].en_ckbox.setChecked(Qt.Qt.Unchecked)


#===============================================================================
# Class DmmWidget
#===============================================================================
class DmmWidget(QWidget):
    """DmmWidget class, main interface of the UI of the data log form.
    """

    CHANNEL_KEYS_LIST = range(101, 123)
    MODULE_SLOT = 1

    def __init__(self):
        """Constructor.
        :returns: None
        """
        super(DmmWidget, self).__init__()
        # Lays out
        tab = QTabWidget()
        self.module_widget = Mod34901Wdgt(self.MODULE_SLOT)
        self.plot_widget = self._build_plot_widget(self.CHANNEL_KEYS_LIST)
        tab.addTab(self.module_widget, "Configuration")
        tab.addTab(self.plot_widget, "Plot data")
        #tab.addTab(self.dev_widget, "Analyze")
        layout = QVBoxLayout()
        layout.addWidget(tab)
        self.setLayout(layout)
        # Initialization
        for legend in self.plot_widget.dict.legends.itervalues():
            legend.setDisabled(True)
        # Local ui handling
        self.module_widget.channel_state_changed.connect( \
            self._channel_state_change)
        self.plot_widget.dict.state_changed.connect(self._update_plot_list)

    @staticmethod
    def _build_plot_widget(channel_keys):
        """Builds widget dedicated to data plotting.
        :param channel_keys: list of key for each of channel in widget (list)
        :returns: data plotting widget (EPlotWidget)
        """
        plot_widget = EPlotWidget(channel_keys)
        plot_widget.plot.setTitle("Monitoring")
        return plot_widget

    @staticmethod
    def _build_dev_widget():
        """Builds layout dedicated to deviation analyze.
        :returns: deviation plotting widget (AdevPlotWidget)
        """
        #dev_widget = DevPlotWidget()
        #return dev_widget
        pass

    @pyqtSlot(int, int)
    def _update_plot_list(self, scan, state):
        """Updates plot list, the list of channel to plot.
        :param scan: the scan number of the channel updated (int)
        :param state: the state of the channel updated (Qt.State)
        :returns: None
        """
        if state == Qt.Qt.Checked:
            self.plot_widget.hide(scan, False)
        else:
            self.plot_widget.hide(scan, True)

    @pyqtSlot(int)
    def _channel_state_change(self, scan):
        """Updates scan list, the list of channel to scan and update legend
        state of plot widget.
        :param scan: scan number of the channel updated (int)
        :returns: None
        """
        state = self.module_widget.channel(scan).checkState()
        if state == Qt.Qt.Checked:
            self.plot_widget.add_item(scan)
            self.plot_widget.legend(scan).setEnabled(True)
            self.plot_widget.legend(scan).setState(Qt.Qt.Checked)
        else:
            self.plot_widget.legend(scan).setDisabled(True)
            self.plot_widget.legend(scan).setState(Qt.Qt.Unchecked)
            self.plot_widget.remove_item(scan)


#===============================================================================
# Class DmmMainWindow
#===============================================================================
class DmmMainWindow(QMainWindow):
    """MainWindow class, main interface of the UI of the data log form.
    """

    def __init__(self):
        """Constructor.
        :returns: None
        """
        super(DmmMainWindow, self).__init__()
        self.setWindowTitle("Dmmger")
        # Lays out
        self._create_actions()
        self._menu_bar = self.menuBar()
        self._populate_menubar()
        self._tool_bar = self.addToolBar("Tool Bar")
        self._populate_toolbar()
        self._tool_bar.setMovable(True)
        self._tool_bar.setFloatable(False)
        self._tool_bar.setAllowedAreas(Qt.Qt.AllToolBarAreas)
        self._status_bar = self.statusBar()
        self._data_log_wdgt = DmmWidget()
        self.setCentralWidget(self._data_log_wdgt)
        # UI handling
        self._ui_handling()
        # Initialization of UI
        self.reset()

    def reset(self):
        """Resets form.
        :returns: None
        """
        self._data_log_wdgt.module_widget.reset()
        self._data_log_wdgt.plot_widget.reset()
        self.action_run.setDisabled(True)
        self.action_save.setDisabled(True)
        self.action_reset.setDisabled(True)

    @property
    def module_widget(self):
        """Getter of module widget (Mod34901Wdgt).
        :returns: a module widget (Mod34901Wdgt)
        """
        return self._data_log_wdgt.module_widget

    @property
    def plot_widget(self):
        """Getter of plot widget (EPlotWidget).
        :returns: a plot widget (EPlotWidget)
        """
        return self._data_log_wdgt.plot_widget

    @property
    def dev_widget(self):
        """Getter of deviation widget (DevPlotWidget).
        :returns: a deviation widget (DevPlotWidget)
        """
        return self._data_log_wdgt.dev_widget

    def _ui_handling(self):
        """Basic (local) ui handling.
        :returns: None
        """
        # Sets run and stop exclusive actions
        self.action_run.triggered.connect( \
            lambda: self.action_stop.setEnabled(True))
        self.action_stop.triggered.connect( \
            lambda: self.action_run.setEnabled(True))
        self.action_run.triggered.connect( \
            lambda: self.action_run.setEnabled(False))
        self.action_stop.triggered.connect( \
            lambda: self.action_stop.setEnabled(False))
        self.action_stop.setEnabled(False)
        # Handles UI when the state of a channel changes
        self._data_log_wdgt.module_widget.channel_state_changed.connect( \
            self._channel_state_change)

    @pyqtSlot()
    def _channel_state_change(self):
        """Handles ui when the state of channels changes:
        updates the state of the run button of bars.
        :returns: None
        """
        if len(self._data_log_wdgt.module_widget.enabled_channels()) == 0:
            # If no channel selected, do not allow start of acquisition
            self.action_run.setDisabled(True)
        else:
            # If channel(s) selected, allow start of acquisition
            self.action_run.setEnabled(True)

    def _create_actions(self):
        """Creates actions used with bar widgets.
        :returns: None
        """
        self.action_save = QAction(QIcon.fromTheme("document-save"), \
                                   self.trUtf8("&Save"), self)
        self.action_save.setStatusTip(self.trUtf8("Save data"))
        self.action_save.setShortcut('Ctrl+S')

        self.action_save_cfg = QAction(self.trUtf8("Save &Config"), self)
        self.action_save_cfg.setStatusTip(self.trUtf8( \
                                        "Save the configuration for later"))
        self.action_save_cfg.setShortcut('Ctrl+C')

        self.action_load_cfg = QAction(self.trUtf8("&Load Config"), self)
        self.action_load_cfg.setStatusTip(self.trUtf8( \
                                        "Load a previous configuration"))
        self.action_load_cfg.setShortcut('Ctrl+L')

        self.action_quit = QAction(QIcon.fromTheme("application-exit"), \
                                   self.trUtf8("&Quit"), self)
        self.action_quit.setStatusTip(self.trUtf8("Exit application"))
        self.action_quit.setShortcut('Ctrl+Q')

        self.action_reset = QAction(QIcon.fromTheme("edit-clear"), \
                                    self.trUtf8("R&eset"), self)
        self.action_reset.setStatusTip(self.trUtf8("Reset the configuration"))
        self.action_reset.setShortcut('Ctrl+E')

        self.action_pref = QAction(QIcon.fromTheme("preferences-system"), \
                                    self.trUtf8("&Preferences"), self)
        self.action_pref.setStatusTip(self.trUtf8( \
                                    "Open preference dialog form"))
        self.action_pref.setShortcut('Ctrl+P')

        self.action_run = QAction(QIcon.fromTheme("system-run"), \
                                  self.trUtf8("&Run"), self)
        self.action_run.setStatusTip(self.trUtf8("Start acquisition"))
        self.action_run.setShortcut('Ctrl+R')

        self.action_stop = QAction(QIcon.fromTheme("process-stop"), \
                                   self.trUtf8("S&top"), self)
        self.action_stop.setStatusTip(self.trUtf8("Stop acquisition"))
        self.action_stop.setShortcut('Ctrl+T')

        self.action_about = QAction(QIcon.fromTheme("help-about"), \
                                    self.trUtf8("A&bout"), self)
        self.action_about.setStatusTip(self.trUtf8("About " + APP_NAME))
        self.action_about.setShortcut('Ctrl+B')

    def _populate_menubar(self):
        """Populates the menu bar of the UI
        :returns: None
        """
        self._menu_bar.menu_file = self._menu_bar.addMenu(self.trUtf8("&File"))
        self._menu_bar.menu_edit = self._menu_bar.addMenu(self.trUtf8("&Edit"))
        self._menu_bar.menu_process = self._menu_bar.addMenu( \
                                        self.trUtf8("&Process"))
        self._menu_bar.menu_help = self._menu_bar.addMenu(self.trUtf8("&Help"))
        self._menu_bar.menu_file.addAction(self.action_save)
        self._menu_bar.menu_file.addSeparator()
        self._menu_bar.menu_file.addAction(self.action_save_cfg)
        self._menu_bar.menu_file.addAction(self.action_load_cfg)
        self._menu_bar.menu_file.addSeparator()
        self._menu_bar.menu_file.addAction(self.action_quit)
        self._menu_bar.menu_edit.addAction(self.action_pref)
        self._menu_bar.menu_process.addAction(self.action_run)
        self._menu_bar.menu_process.addAction(self.action_stop)
        self._menu_bar.menu_process.addAction(self.action_reset)
        self._menu_bar.menu_help.addAction(self.action_about)

    def _populate_toolbar(self):
        """Populates the tool bar of the UI
        :returns: None
        """
        self._tool_bar.addAction(self.action_run)
        self._tool_bar.addAction(self.action_stop)
        self._tool_bar.addAction(self.action_reset)
        self._tool_bar.addAction(self.action_save)


#===============================================================================
def display_ui():
    """Displays the main UI.
    """
    import sys

    def print_slot(arg):
        """Print 'arg' to standard output.
        :param arg: data to display (any)
        :returns: None
        """
        print "ui.print_slot.arg;", arg

    app = QApplication(sys.argv)
    #ui = ChannelWdgt(101, ("DC Voltage", "AC Voltage", "Resistance"))
    #ui = Mod34901Wdgt(1)
    #ui = DmmWidget()
    ui = DmmMainWindow()
    ui.module_widget.channel_state_changed.connect(print_slot)
    ui.show()
    sys.exit(app.exec_())


#===============================================================================
if __name__ == "__main__":
    display_ui()
