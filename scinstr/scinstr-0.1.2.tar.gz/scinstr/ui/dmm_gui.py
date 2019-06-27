#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""package dmm
author  Benoit Dubois
version 0.1
license GPL v3.0+
date    2014-22-05
brief   GUI to handle the 34972A Data Logger via the ethernet interface.
"""

import os
import logging
import tempfile
import numpy as np
from datetime import datetime
from fnmatch import fnmatch
from time import strftime
from PyQt4.QtCore import Qt, pyqtSlot, QObject, QSettings, QThread, QDir, QFileInfo
from PyQt4.QtGui import QMessageBox, QDialog, QFileDialog

import dev34972a as Dev
from utilsben.mjdutils import datetime_to_mjd
from utilsben.datacontainer import TimeSerieContainer
from data_log_form import DmmMainWindow, PreferenceDialog
from dmm.version import __version__
from dmm.dev.constants import ORGANIZATION, APP_NAME, DEF_IP, DEF_PORT, DEF_TIMEOUT


APP_CFG_DIR = QFileInfo(QSettings(ORGANIZATION, APP_NAME).fileName()).absolutePath()


#==============================================================================
# CLASS Dmm34972AGui
#==============================================================================
class Dmm34972AGui(QObject):
    """34972A data logger device Graphical User Interface class.
    GUI over Dev34972A class controller.
    """

    def __init__(self):
        """The constructor.
        :returns: None
        """
        super(Dmm34972AGui, self).__init__()
        settings = QSettings()
        if settings.contains("dev/ip") is False:
            logging.warning("ini file seems empty, " + \
                            "creates one with default values.")
            self._reset_ini()
        ip = settings.value("dev/ip").toString()
        self._data_container = TimeSerieContainer()
        self._acq_start_date = "" # Date @ starting of the acquisition process
        self._tmp_file = ""
        self._ofile = ""
        # Adds ui form
        self._ui = DmmMainWindow()
        # Adds device controller
        self._param_eth = Dev.ParamEth(ip, DEF_PORT, DEF_TIMEOUT)
        self._dev = Dev.Dev34972aWorker(self._param_eth)        
        #self._dev = Stimuli() # For test without the 34972A device
        # Defines behaviour
        self._trigger_ui_actions()
        self._logic_handling()
        # Create producer
        self._prod_thread = QThread()
        self._dev.moveToThread(self._prod_thread)
        self._prod_thread.started.connect(self._dev.start)
        self._dev.finished.connect(self._prod_thread.quit)
        # Shows form
        self._ui.setVisible(True)

    def __del__(self):
        """Stops acquisition properly before exiting application.
        :returns: None
        """
        self._dev.stop()
        self._prod_thread.quit()

    def _logic_handling(self):
        """Defines behaviour of logic.
        :returns: None
        """
        self._dev.new_data.connect(self._write_sample)
        self._dev.new_data.connect(self._update_container)
        self._dev.new_data.connect(self._plot_data)
        # !Only for debug!
        #self._dev.new_data.connect(print_data, Qt.DirectConnection)
        # !Only for debug!
        self._data_container.updated.connect(self._container_updated)
        self._ui.plot_widget.dict.transformations_changed.connect( \
            self._plot_data)
        self._ui.module_widget.channel_state_changed.connect( \
            self._channel_state_change)

    @pyqtSlot()
    def _container_updated(self):
        """Action when data container is updated.
        :returns: None
        """
        if self._data_container.is_empty() is False:
            self._ui.action_save.setEnabled(True)
            self._ui.action_reset.setEnabled(True)
        else:
            self._ui.action_reset.setDisabled(True)

    @pyqtSlot(int)
    def _channel_state_change(self, scan):
        """Updates scan list, the list of channel to scan and update legend
        state of plot widget.
        :param scan: scan number of the channel updated (int)
        :returns: None
        """
        state = self._ui.module_widget.channel(scan).checkState()        
        if state == Qt.Checked:
            self._data_container.add_item(scan)
        else:
            self._data_container.remove_item(scan)

    def set_configuration(self):
        """Sets configuration to real device.
        :returns: None
        """
        for channel in self._ui.module_widget.enabled_channels():
            msg = "CONF:" + Dev.FUNCTION_FULL[channel.func].mnemo \
              + " " + Dev.FUNCTION_FULL[channel.func].list[channel.rang].mnemo
            # Test is used because configuration message syntax needs to be
            # modified if range is in auto mode: User guide indicated that
            # when auto range is used, we must specified "AUTO" for the
            # solution parameter or omit the parameter from the command.
            # But it seems that resolution parameter "AUTO" doesn't work
            # with range parameter "AUTO". So we omit the resolution
            # parameter and thus we must change the message syntax.
            if channel.rang != 0: # ie not "AUTO"
                msg += ", " + Dev.INTGT[channel.intgt].mnemo
            msg += ", (@" + str(channel.id) + ")"
            self._dev.write(msg)

    def set_scanlist(self):
        """Sets scanlist to real device.
        :return: None
        """
        scanlist = ""
        for channel in self._ui.module_widget.enabled_channels():
            scanlist += str(channel.id) + ","
        scanlist = "ROUT:SCAN (@" + scanlist[:-1] + ")"
        try:
            self._dev.write(scanlist)
        except Exception as ex:
            logging.error(str(ex))
            raise

    @pyqtSlot()
    def _reset_ui(self):
        """Clears application: resets user interface to starting state.
        :returns: None
        """
        self._ui.reset()
        self._data_container.reset()

    @pyqtSlot()
    def _quit(self):
        """Quits application.
        :returns: None
        """
        self._dev.stop()
        self._ui.close()

    @pyqtSlot()
    def _start_acq(self):
        """Starts acquisition process.
        :returns: None
        """
        try:
            self._dev.connect()
        except Exception as ex:
            logging.warning("Connection to device failled: %s" % ex)
            return
        self._data_container.clear_data()
        self._ui.module_widget.setDisabled(True)
        self.set_configuration()
        self.set_scanlist()
        self._acq_start_date = strftime("%Y%m%d-%H%M%S")
        self._tmp_file = self._acq_start_date  + ".dat"
        header = self._make_header()
        with open(APP_CFG_DIR + self._tmp_file, 'a', 0) as fd:
            np.savetxt(fname=fd, X=np.empty([0, 0]), header=header)        
        self._prod_thread.start()        

    @pyqtSlot()
    def _stop_acq(self):
        """Stops acquisition request process.
        :returns: None
        """
        self._dev.stop()
        self._dev.close()
        btn_val = self._save_box()
        if btn_val == QMessageBox.Yes: # Stop acquisition and save data
            self._save()
        # In fact saves the last temporary data file, one never knows...
        # But before we move the oldest data files to system temp directory:
        for fd in os.listdir(APP_CFG_DIR):
            if fnmatch(fd, "*.dat.old"):
                os.rename(APP_CFG_DIR + fd, tempfile.tempdir + fd)
        os.rename(APP_CFG_DIR + self._tmp_file, \
                    APP_CFG_DIR + self._tmp_file + ".old")
        self._ui.module_widget.setEnabled(True)

    @pyqtSlot()
    def _save(self):
        """Save data method. Call a file dialog box to choose a filename
        for the data file.
        :returns: True if data are saved else False (bool)
        """
        self._ofile = QFileDialog().getSaveFileName(parent=None, \
                        caption=self.trUtf8("Save data"), \
                        directory=QDir.currentPath(), \
                        filter=self.trUtf8("Data files (*.dat);;Any files (*)"))
        if self._ofile == "":
            return False # Aborts if no file given
        header = self._make_header()
        data = self._data_container.data()
        with open(self._ofile, 'w', 0) as fd:
            np.savetxt(fname=fd, X=data, delimiter='\t', header=header)
        return True

    @pyqtSlot()
    def _save_cfg(self):
        """Saves current device configuration. Call a file dialog box to give
        a filename for the config file.
        :returns: True if config is saved else False (bool)
        """
        cfg_file = QFileDialog().getSaveFileName(None, \
                        self.trUtf8("Save configuration"), \
                        QDir.currentPath(), \
                        self.trUtf8(";;Config files (*.cfg);;Any files (*)"))
        if cfg_file == "":
            return False # Aborts if no file given
        cfg = QSettings(cfg_file, QSettings.IniFormat, self)
        for channel in self._ui.module_widget.itervalues():
            if channel.checkState() == Qt.Checked:
                ch_nb = str(channel.id)
                func = channel.func
                rang = channel.rang
                reso = channel.reso
                cfg.beginGroup(ch_nb)
                cfg.setValue("function", func)
                cfg.setValue("range", rang)
                cfg.setValue("resolution", reso)
                cfg.endGroup()
        return True

    @pyqtSlot()
    def _load_cfg(self):
        """Loads a device configuration. Call a file dialog box to select
        the config file.
        :returns: True if config is loaded else False (bool)
        """
        cfg_file = QFileDialog().getOpenFileName(None, \
                        self.trUtf8("Load configuration"), \
                        QDir.currentPath(), \
                        self.trUtf8("Config files (*.cfg);;Any files (*)"))
        if cfg_file == "":
            return False # Aborts if no file given
        cfg = QSettings(cfg_file, QSettings.IniFormat, self)
        for channel in self._ui.module_widget:
            ch_nb = str(channel.id)
            if cfg.childGroups().contains(ch_nb) is True:
                cfg.beginGroup(ch_nb)
                func = cfg.value("function").toInt()[0]
                rang = cfg.value("range").toInt()[0]
                reso = cfg.value("resolution").toInt()[0]
                cfg.endGroup()
                channel.setState(Qt.Checked)
                channel.set_func(func)
                channel.set_rang(rang)
                channel.set_reso(reso)
            else:
                channel.reset()
        return True

    def _make_header(self):
        """Collects data information (channel, measurement type and parameters)
        to be used as header for a data file.
        :returns: the data header (str)
        """
        now = "Date " + self._acq_start_date + "\n"
        channel_info = ""
        for channel in self._ui.module_widget.channels.itervalues():
            if channel.checkState() == Qt.Checked:
                ch_nb = str(channel.id)
                func = str(channel.param_wdgt.func_cbox.currentText())
                rang = str(channel.param_wdgt.rang_cbox.currentText ())
                reso = str(channel.param_wdgt.reso_cbox.currentText ())
                channel_info += "Channel(" + ch_nb + ");" + func + ";" + \
                  rang + ";" + reso + "\n"
        header = now + channel_info
        return header

    @pyqtSlot(str)
    def _write_sample(self, sample):
        """Writes the current sample(s) in a file.
        :param sample: sample(s) to write (str)
        :returns: None
        """
        now = datetime.utcnow()
        settings = QSettings()
        if settings.value("file/mjd").toBool() is True:
            now = datetime_to_mjd(now)
        sample_list = str(sample).split(',')
        sample_list.insert(0, str(now))
        asample = np.array(sample_list, dtype=float , ndmin=2)
        with open(APP_CFG_DIR + self._tmp_file, 'a', 0) as fd:
            np.savetxt(fname=fd, X=asample, delimiter='\t')

    @pyqtSlot(str)
    def _update_container(self, sample):
        """Adds the current sample(s) to the data container.
        :param sample: sample(s) to add to data container (str)
        :returns: None
        """
        now = datetime_to_mjd(datetime.utcnow())
        self._data_container.add_sample("time", [now])
        enabled_channel_list = self._ui.module_widget.enabled_channels()
        sample_list = str(sample).split(',')
        sample_list.reverse()
        for channel in enabled_channel_list:
            data = np.array([float(sample_list.pop())])
            self._data_container.add_sample(channel.id, data)

    @pyqtSlot()
    def _plot_data(self):
        """Plots data on graph.
        :returns: None
        """
        for key, legend in self._ui.plot_widget.dict.iteritems():
            if legend.checkState() == Qt.Checked:
                scale = legend.transformations.scale
                offset = legend.transformations.offset
                datax = self._data_container.data("time")
                datay = self._data_container.data(key) * scale + offset
                data = np.column_stack((np.transpose(datax),
                                        np.transpose(datay)))
                try:
                    self._ui.plot_widget.curve(key).setData(data)
                except ZeroDivisionError:
                    logging.debug("Divide by zero")
                except ValueError as ex:
                    logging.warning("Exception: %s", str(ex))
                except Exception as ex:
                    logging.warning("Exception: %s", str(ex))
        
    def _reset_ini(self):
        """Resets the ini file with default values.
        :returns: None
        """
        settings = QSettings()
        settings.setValue("dev/ip", DEF_IP)
        settings.setValue("file/mjd", False)

    @pyqtSlot()
    def _preference(self):
        """Displays the preference message box.
        :returns: None
        """
        settings = QSettings()
        dialog = PreferenceDialog(settings.value("dev/ip").toString(),
                                  settings.value("file/mjd").toBool())
        dialog.setParent(None, Qt.Dialog)
        retval = dialog.exec_()
        if retval == QDialog.Accepted:
            settings.setValue("dev/ip", dialog.ip)
            settings.setValue("file/mjd", dialog.mjd)

    @pyqtSlot()
    def _about(self):
        """Displays an about message box.
        :returns: None
        """
        QMessageBox.about(None, self.trUtf8("About " + APP_NAME), \
                          self.trUtf8("<b>" + APP_NAME + "</b> " + \
                          __version__ + "<br>"
                          "GUI dedicated to handle the 34972A device.<br>"
                          "Author Benoit Dubois, benoit.dubois@femto-st.fr.<br>"
                          "Copyright FEMTO Engineering.<br>"
                          "Licensed under the GNU GPL v3.0 or upper."))

    def _save_box(self):
        """Displays a message box requesting confirmation to save the data file.
        Returns the value of the button clicked.
        :returns: the value of the button clicked (int)
        """
        msg_box = QMessageBox()
        msg_box.setWindowTitle(self.trUtf8(APP_NAME))
        msg_box.setText(self.trUtf8("Acquisition stopped"))
        msg_box.setInformativeText(self.trUtf8("Save data?"))
        msg_box.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
        msg_box.setDefaultButton(QMessageBox.Yes)
        btn_val = msg_box.exec_()
        return btn_val

    def _trigger_ui_actions(self):
        """Triggers ui actions: connects actions of ui with real actions.
        :returns: None
        """
        self._ui.action_run.triggered.connect(self._start_acq)
        self._ui.action_stop.triggered.connect(self._stop_acq)
        self._ui.action_save.triggered.connect(self._save)
        self._ui.action_save_cfg.triggered.connect(self._save_cfg)
        self._ui.action_load_cfg.triggered.connect(self._load_cfg)
        self._ui.action_quit.triggered.connect(self._quit)
        self._ui.action_reset.triggered.connect(self._reset_ui)
        self._ui.action_pref.triggered.connect(self._preference)
        # lambda is needed due to un unexplicated bug in action handling:
        # if lambda is not used, no actions work.
        self._ui.action_about.triggered.connect(lambda: self._about())



