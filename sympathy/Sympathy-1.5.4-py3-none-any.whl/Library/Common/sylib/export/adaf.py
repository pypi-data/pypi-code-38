# -*- coding:utf-8 -*-
# Copyright (c) 2017, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import os
from sympathy.api import qt as qt_compat
from sympathy.api import node as synode
from sympathy.api import exporters
QtGui = qt_compat.import_module('QtGui')


class ADAFDataExporterBase(exporters.DataExporterBase):

    @classmethod
    def _create_filename_using_column(cls, parameter_root, adaf_file):
        column_name = parameter_root['column_as_name'].selected
        meta_value = adaf_file.meta[column_name].value()
        if meta_value is None:
            meta_value = adaf_file.meta[column_name].value()

        if len(meta_value) > 0:
            return meta_value[0]
        else:
            return None

    @classmethod
    def _create_filename_using_strategy(cls, parameter_root,
                                        input_list):
        selected_strategy_name = parameter_root['selected_strategy'].selected
        filename_wo_ext = None
        if (selected_strategy_name ==
                TabbedADAFDataExporterBase.filename_source_strategy):
            filename_wo_ext = input_list.source_id()
        elif (selected_strategy_name ==
              TabbedADAFDataExporterBase.filename_column_strategy):
            filename_wo_ext = cls._create_filename_using_column(
                parameter_root, input_list)

        filename_extension = parameter_root['filename_extension'].value
        filename = u'{0}{1}{2}'.format(
            filename_wo_ext, os.path.extsep, filename_extension)
        return filename

    @classmethod
    def _create_filenames(cls, parameter_root, input_list):
        created_filenames = []
        try:
            for adaf_file in input_list:
                created_filenames.append(
                    cls._create_filename_using_strategy(
                        parameter_root, adaf_file))
        except IOError:
            pass
        return created_filenames

    def create_filenames(self, input_list, filename, *args):
        """Return a list of filenames that will be exported to."""
        if not self.file_based():
            return super(ADAFDataExporterBase,
                         self).create_filenames(input_list, filename, *args)

        use_filename_strategy = self._parameters[
            'use_filename_strategy'].value

        if use_filename_strategy:
            filenames = self._create_filenames(
                self._parameters, input_list)
            if filenames:
                return filenames
            else:
                return ['Cannot preview filenames']

        return super(ADAFDataExporterBase,
                     self).create_filenames(input_list, filename, *args)


def get_column_from_adaf_list(input_list, group):
    if input_list.is_valid():
        adaf_file = []
        if len(input_list):
            adaf_file = input_list[0]
        try:
            return sorted(getattr(adaf_file, group).keys())
        except Exception:
            return []
    else:
        return []


class FilenameStrategy(object):
    def __init__(self, name, widget):
        self._name = name
        self._widget = widget

    def name(self):
        return self._name

    def widget(self):
        return self._widget


class StackedStrategyWidget(QtGui.QWidget):
    filename_changed = qt_compat.Signal()

    def __init__(self, parameter_root, filename_strategies=None, parent=None):
        super(StackedStrategyWidget, self).__init__(parent)
        self._parameter_root = parameter_root

        self._filename_strategies = (
            [] if filename_strategies is None else filename_strategies)
        self._init_gui()

    def _init_gui(self):
        vlayout = QtGui.QVBoxLayout()
        vlayout.setContentsMargins(0, 0, 0, 0)
        strategy_vlayout = QtGui.QVBoxLayout()
        self._strategy_groupbox = QtGui.QGroupBox("Strategy")
        self._strategy_groupbox.setLayout(strategy_vlayout)

        self._strategy_stackwidget = QtGui.QStackedWidget()

        # Init GUI before the widgets are created
        self._pre_init_gui_from_parameters()

        self._use_filename_strategy_widget = (
            self._parameter_root['use_filename_strategy'].gui())

        self._strategy_widget = (
            self._parameter_root['selected_strategy'].gui())

        self._strategy_combobox = self._strategy_widget.editor().combobox()

        self._post_init_gui_from_parameters()

        vlayout.addWidget(self._use_filename_strategy_widget)
        strategy_vlayout.addWidget(self._strategy_widget)
        strategy_vlayout.addWidget(self._strategy_stackwidget)
        vlayout.addWidget(self._strategy_groupbox)
        self.setLayout(vlayout)

        self._use_filename_strategy_widget.stateChanged[int].connect(
            self._state_changed)
        self._strategy_combobox.currentIndexChanged[int].connect(
            self._strategy_combo_changed)
        self._strategy_stackwidget.currentChanged[int].connect(
            self._tab_changed)

    def _pre_init_gui_from_parameters(self):
        self._parameter_root['selected_strategy'].list = list(
            TabbedADAFDataExporterBase.filename_strategies)
        for filename_strategy in self._filename_strategies:
            self.add_strategy(filename_strategy)

    def _post_init_gui_from_parameters(self):
        use_filename_strategy = (
            self._parameter_root['use_filename_strategy'].value)
        self._strategy_groupbox.setEnabled(use_filename_strategy)
        selected_strategy_name = (
            self._parameter_root['selected_strategy'].selected)
        index = self._strategy_combobox.findText(selected_strategy_name)
        if -1 == index:
            index = 0
        self._strategy_stackwidget.setCurrentIndex(index)

    def add_strategy(self, filename_strategy):
        self._strategy_stackwidget.addWidget(
            filename_strategy.widget())

    def _strategy_combo_changed(self, index):
        self._strategy_stackwidget.setCurrentIndex(index)
        self.filename_changed.emit()

    def _tab_changed(self, index):
        self._strategy_combobox.setCurrentIndex(index)
        self.filename_changed.emit()

    def _state_changed(self, state):
        self._strategy_groupbox.setEnabled(
            self._parameter_root['use_filename_strategy'].value)
        self.filename_changed.emit()

    def _filename_changed(self):
        self.filename_changed.emit()


class TabbedADAFDataExporterBase(ADAFDataExporterBase):

    filename_strategies = (filename_source_strategy,
                           filename_column_strategy) = (
                               "Source identifier as name",
                               "Column as name")

    def __init__(self, parameters):
        super(TabbedADAFDataExporterBase, self).__init__(parameters)

        if 'use_filename_strategy' not in parameters:
            parameters.set_boolean(
                "use_filename_strategy", label="Use filename strategy",
                description="Use a strategy to create the filename(s).")

        if 'selected_strategy' not in parameters:
            parameters.set_list(
                "selected_strategy",
                label="Selected strategy",
                description="The selected filename strategy.",
                plist=list(self.filename_strategies),
                editor=synode.Util.combo_editor())

        if 'column_as_name' not in parameters:
            parameters.set_list(
                "column_as_name",
                label="Meta column",
                editor=synode.Util.combo_editor())


class TabbedDataExportWidget(QtGui.QWidget):
    filename_changed = qt_compat.Signal()

    def __init__(self, parameter_root, input_list):
        super(TabbedDataExportWidget, self).__init__()
        self._parameter_root = parameter_root
        self._input_list = input_list
        self._filename_strategies = []
        self._init_parameters()
        self._init_gui()

    def _init_parameters(self):
        # Init GUI before the widgets are created
        self._init_gui_from_parameters()

        self._column_as_name_widget = (
            self._parameter_root['column_as_name'].gui())

        self._filename_strategies = [
            FilenameStrategy(
                TabbedADAFDataExporterBase.filename_source_strategy,
                QtGui.QWidget()),
            FilenameStrategy(
                TabbedADAFDataExporterBase.filename_column_strategy,
                self._column_as_name_widget)]

        self._tabbed_strategy_widget = StackedStrategyWidget(
            self._parameter_root, self._filename_strategies)

        self._tabbed_strategy_widget.filename_changed.connect(
            self._filename_changed)

        self._column_combobox = self._column_as_name_widget.editor().combobox()
        self._column_combobox.currentIndexChanged[int].connect(
            self._filename_changed)

    def _init_gui(self):
        vlayout = QtGui.QVBoxLayout()
        vlayout.setContentsMargins(0, 0, 0, 0)
        vlayout.addWidget(self._tabbed_strategy_widget)
        self.setLayout(vlayout)

    def _init_gui_from_parameters(self):
        meta_columns = get_column_from_adaf_list(
            self._input_list, 'meta')
        column_as_name = self._parameter_root['column_as_name']
        value_names = column_as_name.value_names[:]
        column_as_name.list = (
            [name for name in value_names
             if name not in meta_columns] +
            meta_columns)

        selected_column_name = column_as_name.selected
        column_list = column_as_name.list
        if not selected_column_name and len(column_list):
            column_as_name.selected = column_as_name.list[0]

    def _filename_changed(self):
        self.filename_changed.emit()
