# Copyright (c) 2013, Combine Control Systems AB
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
"""
This Sympathy module includes the configuration GUI for import of data from
an Excel xls-file.
"""
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import six
from sympathy.platform import qt_compat
from sympathy.utils import dtypes
from sympathy.platform.widget_library import BasePreviewTable
from sympathy.platform.table_viewer import TableModel

QtCore = qt_compat.QtCore  # noqa
QtGui = qt_compat.import_module('QtGui')  # noqa

from . table_sources import tablesource_model_factory, CODEC_LANGS


class TableImportWidget(QtGui.QWidget):
    """
    This Sympathy support class sets up the configuration gui for import
    of data from an Excel xls-file or an ordinary csv-file.
    """

    def __init__(self, parameters, fq_infilename, mode, valid=True,
                 parent=None):
        super(TableImportWidget, self).__init__(parent)

        self.model = tablesource_model_factory(parameters, fq_infilename, mode,
                                               valid)

        self._init_gui(self.model, mode, valid)

    def _init_gui(self, model, mode, valid):
        """Initialize GUI structure."""
        layout = QtGui.QVBoxLayout()
        tab_widget = QtGui.QTabWidget()

        import_parameters = self._collect_import_parameters_widget(
            model)
        tab_widget.addTab(import_parameters, 'Import Parameters')

        table_source = self._collect_table_source_widget(model)
        tab_widget.addTab(table_source, 'Table Source')

        layout.addWidget(tab_widget)

        preview_table = PreviewGroupBoxWidget(model)
        layout.addWidget(preview_table)

        if mode == 'CSV':
            layout.addWidget(model.exceptions_mode.gui())

        self.controller = self._collect_controller(
            model=model,
            table_source=table_source,
            import_param=import_parameters,
            preview_table=preview_table, valid=valid)

        self.setLayout(layout)
        self.adjustSize()

    def _collect_import_parameters_widget(self, model):
        return ImportParametersWidget(model)

    def _collect_table_source_widget(self, model):
        pass

    def _collect_controller(self, **kwargs):
        pass

    def cleanup(self):
        self.model.cleanup()


class TableImportWidgetCSV(TableImportWidget):
    """ """
    MODE = 'CSV'

    def __init__(self, parameters, fq_infilename, valid=True):
        super(TableImportWidgetCSV, self).__init__(
            parameters, fq_infilename, self.MODE, valid)

    def _collect_table_source_widget(self, model):
        return TableSourceWidgetCSV(model)

    def _collect_controller(self, **kwargs):
        """ """
        return TableImportControllerCSV(**kwargs)


class TableImportWidgetXLS(TableImportWidget):
    """ """
    MODE = 'XLS'

    def __init__(self, parameters, fq_infilename, valid=True):
        super(TableImportWidgetXLS, self).__init__(
            parameters, fq_infilename, self.MODE, valid)

    def _collect_table_source_widget(self, model):
        return TableSourceWidgetXLS(model)

    def _collect_controller(self, **kwargs):
        """ """
        return TableImportControllerXLS(**kwargs)


class TableImportWidgetMAT(TableImportWidget):
    """ """
    MODE = 'MAT'

    def __init__(self, parameters, fq_infilename, valid=True):
        super(TableImportWidgetMAT, self).__init__(
            parameters, fq_infilename, self.MODE, valid)

    def _collect_import_parameters_widget(self, model):
        return ImportParametersWidgetMAT(model)

    def _collect_table_source_widget(self, model):
        pass

    def _collect_controller(self, **kwargs):
        """ Preview"""
        return TableImportController(**kwargs)


class TableImportController(object):
    """ """
    def __init__(self, **kwargs):
        self._model = kwargs['model']
        self._table_source = kwargs['table_source']
        self._import_param = kwargs['import_param']
        self._preview_table = kwargs['preview_table']
        self._valid = kwargs['valid']

        self._model.update_table.connect(self._preview_table.update_table)

        self._preview_table.get_preview.connect(
            self._model.collect_preview_values)
        self._import_param.get_preview.connect(
            self._model.collect_preview_values)


class TableImportControllerCSV(TableImportController):
    """ """
    def __init__(self, **kwargs):
        super(TableImportControllerCSV, self).__init__(**kwargs)
        if self._valid:
            self._table_source.delimiter_changed[str].connect(
                self._model.set_delimiter)

            self._table_source.encoding_changed[str].connect(
                self._model.set_encoding)

            self._table_source.quotation_state_changed.connect(
                self._model.set_double_quotations)

            self._table_source.new_custom_delimiter[six.text_type].connect(
                self._model.set_new_custom_delimiter)


class TableImportControllerXLS(TableImportController):
    """ """
    def __init__(self, **kwargs):
        super(TableImportControllerXLS, self).__init__(**kwargs)

        self._table_source.transpose_state_changed.connect(
            self._model.collect_preview_values)

        self._table_source.worksheet_changed[int].connect(
            self._model.collect_preview_values)


def offset_spinbox(parameter, offset):
    spinbox = QtGui.QSpinBox()
    spinbox.setToolTip(parameter.description or '')
    spinbox.setRange(parameter.editor['min'] + offset,
                     parameter.editor['max'] + offset)
    spinbox.setValue(parameter.value + offset)
    spinbox.valueChanged.connect(
        lambda value: setattr(parameter, 'value', value - offset))
    return spinbox


class ImportParametersWidget(QtGui.QWidget):
    """
    The control group box includes the widgets for determination of header
    row/column, unit row/column , description row/column, data start and end
    row/column and transpose condition.
    """

    get_preview = QtCore.Signal()

    def __init__(self, model, parent=None):
        super(ImportParametersWidget, self).__init__(parent)
        self._model = model
        self._init_gui(model)
        self._init_preview_signals()

    def _init_gui(self, model):
        layout = QtGui.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignLeft)

        grid_layout = QtGui.QGridLayout()
        grid_layout.setHorizontalSpacing(20)
        grid_row = 0

        # Headers
        self._headers_checkbox = model.headers.gui()
        self._headers_row_spinbox = offset_spinbox(model.header_row, -1)
        self._old_header_row = model.header_row.value

        self._headers_label = QtGui.QLabel('Headers at row ')

        grid_layout.addWidget(self._headers_checkbox, grid_row, 0)
        grid_layout.addWidget(self._headers_label, grid_row, 1)
        grid_layout.addWidget(self._headers_row_spinbox, grid_row, 2)
        grid_row += 1

        self._headers_row_spinbox.setEnabled(model.headers.value)
        self._headers_label.setEnabled(model.headers.value)

        self._headers_checkbox.stateChanged[int].connect(
            self._headers_state_changed)

        # Units
        self._units_checkbox = model.units.gui()
        self._units_row_spinbox = offset_spinbox(model.unit_row, -1)

        self._units_label = QtGui.QLabel('Units at row')

        grid_layout.addWidget(self._units_checkbox, grid_row, 0)
        grid_layout.addWidget(self._units_label, grid_row, 1)
        grid_layout.addWidget(self._units_row_spinbox, grid_row, 2)
        grid_row += 1

        self._units_row_spinbox.setEnabled(model.units.value)
        self._units_label.setEnabled(model.units.value)

        self._units_row_spinbox.setEnabled(model.units.value)
        self._units_checkbox.stateChanged[int].connect(
            self._units_state_changed)

        # Descriptions
        self._descriptions_checkbox = model.descriptions.gui()
        self._descriptions_row_spinbox = offset_spinbox(
            model.description_row, -1)

        self._descriptions_label = QtGui.QLabel('Descriptions at row')

        grid_layout.addWidget(self._descriptions_checkbox, grid_row, 0)
        grid_layout.addWidget(self._descriptions_label, grid_row, 1)
        grid_layout.addWidget(self._descriptions_row_spinbox, grid_row, 2)
        grid_row += 1

        self._descriptions_row_spinbox.setEnabled(model.descriptions.value)
        self._descriptions_label.setEnabled(model.descriptions.value)

        self._descriptions_row_spinbox.setEnabled(model.descriptions.value)
        self._descriptions_checkbox.stateChanged[int].connect(
            self._descriptions_state_changed)

        # Data
        self._data_offset_spinbox = offset_spinbox(model.data_offset, -1)
        self._data_read_selection = model.data_read_selection.gui()
        self._data_rows_spinbox = offset_spinbox(model.data_rows, 0)

        grid_row += 1

        data_start_label = QtGui.QLabel('Data start at row')

        grid_layout.addWidget(data_start_label, grid_row, 1)
        grid_layout.addWidget(self._data_offset_spinbox, grid_row, 2)
        grid_layout.addWidget(self._data_read_selection, grid_row, 3)
        grid_layout.addWidget(self._data_rows_spinbox, grid_row, 4)

        layout.addLayout(grid_layout)

        self.setLayout(layout)

    def _init_preview_signals(self):
        signals = [
            self._headers_checkbox.valueChanged,
            self._headers_row_spinbox.valueChanged,
            self._units_row_spinbox.valueChanged,
            self._units_checkbox.valueChanged,
            self._descriptions_row_spinbox.valueChanged,
            self._descriptions_checkbox.valueChanged,
            self._data_offset_spinbox.valueChanged,
            self._data_rows_spinbox.valueChanged]
        for signal in signals:
            signal.connect(self.get_preview)

    @qt_compat.Slot(int)
    def _headers_state_changed(self, value):
        self._headers_row_spinbox.setEnabled(self._model.headers.value)
        self._headers_label.setEnabled(self._model.headers.value)

    @qt_compat.Slot(int)
    def _units_state_changed(self, value):
        self._units_row_spinbox.setEnabled(self._model.units.value)
        self._units_label.setEnabled(self._model.units.value)

    @qt_compat.Slot(int)
    def _descriptions_state_changed(self, value):
        self._descriptions_row_spinbox.setEnabled(
            self._model.descriptions.value)
        self._descriptions_label.setEnabled(self._model.descriptions.value)


class ImportParametersWidgetMAT(QtGui.QWidget):
    """
    The control group box includes the widgets for determination of
    data start and end row/column and transpose condition.
    """

    get_preview = QtCore.Signal()

    def __init__(self, model, parent=None):
        super(ImportParametersWidgetMAT, self).__init__(parent)
        self._model = model
        self._init_gui(model)
        self._init_preview_signals()

    def _init_gui(self, model):
        layout = QtGui.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignLeft)

        grid_layout = QtGui.QGridLayout()
        grid_layout.setHorizontalSpacing(20)
        grid_row = 0

        # Data
        self._data_offset_spinbox = offset_spinbox(model.data_offset, -1)

        self._data_read_selection = model.data_read_selection.gui()
        self._data_rows_spinbox = offset_spinbox(model.data_rows, -1)

        grid_row += 1
        data_start_label = QtGui.QLabel('Data start at row')

        grid_layout.addWidget(data_start_label, grid_row, 1)
        grid_layout.addWidget(self._data_offset_spinbox, grid_row, 2)
        grid_layout.addWidget(self._data_read_selection, grid_row, 3)
        grid_layout.addWidget(self._data_rows_spinbox, grid_row, 4)

        layout.addLayout(grid_layout)

        self.setLayout(layout)

    def _init_preview_signals(self):
        signals = [
            self._data_offset_spinbox.valueChanged,
            self._data_rows_spinbox.valueChanged]
        for signal in signals:
            signal.connect(self.get_preview)


class PreviewModel(TableModel):
    def __init__(self, *args, **kwargs):
        super(PreviewModel, self).__init__(*args, **kwargs)
        self._start_row = 0

    def set_table_data(self, table_data, start_row=0):
        self._start_row = start_row
        self.set_table(table_data)

    def headerData(self, section, orientation, role):  # noqa
        if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return self._start_row + section - 1
        return super(PreviewModel, self).headerData(section, orientation, role)


class PreviewGroupBoxWidget(QtGui.QGroupBox):
    get_preview = qt_compat.Signal()

    """
    This GroupBox includes widgets for determination of preview parameters
    and a preview table.
    """
    def __init__(self, model, title='', parent=None):
        super(PreviewGroupBoxWidget, self).__init__(title, parent)
        self._model = model
        self._init_gui(model)

    def _init_gui(self, model):
        layout = QtGui.QVBoxLayout()

        # Preview Range
        preview_range_layout = QtGui.QHBoxLayout()
        preview_range_layout.setAlignment(QtCore.Qt.AlignLeft)
        self._preview_start_row_spinbox = offset_spinbox(
            model.preview_start_row, -1)
        self._no_preview_rows_spinbox = model.no_preview_rows.gui()

        preview_range_layout.addWidget(self._no_preview_rows_spinbox)

        layout.addLayout(preview_range_layout)

        # Preview table

        self._preview_table = BasePreviewTable()
        self._preview_table_model = PreviewModel()
        self._preview_table.setModel(self._preview_table_model)

        self._preview_table.setMinimumSize(545, 100)
        self._preview_table.setEditTriggers(
            QtGui.QAbstractItemView.NoEditTriggers)
        self._preview_table.setSelectionBehavior(
            QtGui.QAbstractItemView.SelectItems)
        self._preview_table.setSelectionMode(
            QtGui.QAbstractItemView.NoSelection)
        self._preview_table.ScrollHint(
            QtGui.QAbstractItemView.EnsureVisible)
        # self._preview_table.setCornerButtonEnabled(True)
        # self._preview_table.setShowGrid(True)
        # self._preview_table.setAlternatingRowColors(True)
        # self._preview_table_model = PreviewModel()
        # self._preview_table.setModel(self._preview_table_model)

        self._stacked_widget = QtGui.QStackedWidget()
        self._no_preview = QtGui.QLabel("Building preview...")
        self._no_preview.setAlignment(QtCore.Qt.AlignCenter)
        # Order of adding widgets is used by show_preview/hide_preview methods
        self._stacked_widget.addWidget(self._no_preview)
        self._stacked_widget.addWidget(self._preview_table)

        layout.addWidget(self._stacked_widget)

        signals = [
            self._preview_start_row_spinbox.valueChanged,
            self._no_preview_rows_spinbox.editor().valueChanged]
        for signal in signals:
            signal.connect(self.hide_preview)
            signal.connect(self.get_preview)

        if model.data_table is not None:
            self.update_table()

        self.setLayout(layout)

    @qt_compat.Slot()
    def hide_preview(self):
        self._stacked_widget.setCurrentIndex(0)

    @qt_compat.Slot()
    def show_preview(self):
        self._stacked_widget.setCurrentIndex(1)

    @qt_compat.Slot()
    def update_table(self):
        """ """
        if self._model.data_table is None:
            self.hide_preview()
            return
        else:
            self.show_preview()

        start_row = self._model.data_offset.value
        self._preview_table_model.set_table_data(
            self._model.data_table, start_row)


class TableSourceWidgetCSV(QtGui.QWidget):
    """ """
    delimiter_changed = qt_compat.Signal(str)
    new_custom_delimiter = qt_compat.Signal(str)
    transpose_state_changed = qt_compat.Signal(int)
    encoding_changed = qt_compat.Signal(str)
    quotation_state_changed = qt_compat.Signal(int)

    def __init__(self, model, parent=None):
        super(TableSourceWidgetCSV, self).__init__(parent)

        self._init_gui(model)

    def _init_gui(self, model):
        layout = QtGui.QVBoxLayout()

        self._encoding_combobox = QtGui.QComboBox()
        self._encoding_combobox.addItems(sorted(CODEC_LANGS.keys()))
        self._encoding_combobox.setToolTip(
            'Select text coding in table source')
        self._encoding_combobox.setCurrentIndex(
            sorted(CODEC_LANGS.keys()).index(model.encoding_key))
        self._delimiter_buttons = DelimiterWidget(model, model.delimiter_key)

        encoding_layout = QtGui.QHBoxLayout()
        encoding_layout.setAlignment(QtCore.Qt.AlignLeft)
        encoding_layout.setSpacing(20)

        encoding_label = QtGui.QLabel('Table source encoding')
        encoding_label.setBuddy(self._encoding_combobox)
        encoding_layout.addWidget(encoding_label)
        encoding_layout.addWidget(self._encoding_combobox)

        layout.addLayout(encoding_layout)
        layout.addWidget(self._delimiter_buttons)

        self._delimiter_buttons.delimiter_buttons_clicked[str].connect(
            self.delimiter_changed)

        self._delimiter_buttons.new_custom_delimiter[str].connect(
            self.new_custom_delimiter)

        self._encoding_combobox.currentIndexChanged[str].connect(
            self.encoding_changed)

        self.setLayout(layout)


class DelimiterWidget(QtGui.QWidget):
    """ """
    delimiter_buttons_clicked = qt_compat.Signal(str)
    new_custom_delimiter = qt_compat.Signal(six.text_type)

    def __init__(self, model, delimiter_key, parent=None):
        super(DelimiterWidget, self).__init__(parent)

        self._init_gui(model, delimiter_key)

    def _init_gui(self, model, delimiter_key):
        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(QtCore.Qt.AlignLeft)
        layout.setSpacing(20)

        delimiter_label = QtGui.QLabel('Delimiter')
        layout.addWidget(delimiter_label)

        checkbox_container = []
        checkbox_container.append(QtGui.QCheckBox('Tab'))
        checkbox_container.append(QtGui.QCheckBox('Comma'))
        checkbox_container.append(QtGui.QCheckBox('Semicolon'))
        checkbox_container.append(QtGui.QCheckBox('Space'))
        checkbox_container.append(QtGui.QCheckBox('Other'))

        self._delimiter_button_group = QtGui.QButtonGroup()
        self._delimiter_button_group.setExclusive(True)
        checkbox_labels = []
        for checkbox in checkbox_container:
            layout.addWidget(checkbox)
            self._delimiter_button_group.addButton(checkbox)
            checkbox_labels.append(str(checkbox.text()))

        self._custom_delimiter_linedit = QtGui.QLineEdit()
        self._custom_delimiter_linedit.setFixedWidth(50)
        self._custom_delimiter_linedit.setMaxLength(1)
        self._custom_delimiter_linedit.setText(
            model.custom_delimiter.value)
        self._custom_delimiter_linedit.setToolTip(
            'An arbitrary one-character string as delimiter.')

        layout.addWidget(self._custom_delimiter_linedit)

        self._delimiter_button_group.buttons()[
            checkbox_labels.index(delimiter_key)].setChecked(True)

        self._custom_delimiter_linedit.setEnabled(
            self._delimiter_button_group.buttons()[-1].isChecked())

        self._delimiter_button_group.buttonClicked.connect(
            self._delimiter_changed)

        self._custom_delimiter_linedit.textChanged[six.text_type].connect(
            self.new_custom_delimiter)

        checkbox_container[-1].stateChanged[int].connect(
            self._custom_listedit_enabled)

        self.setLayout(layout)

    def _delimiter_changed(self, checkbox):
        checkbox_label = str(checkbox.text())
        self.delimiter_buttons_clicked.emit(checkbox_label)

    @qt_compat.Slot(int)
    def _custom_listedit_enabled(self, value):
        self._custom_delimiter_linedit.setEnabled(value)


class TableSourceWidgetXLS(QtGui.QWidget):
    """ """
    worksheet_changed = qt_compat.Signal(int)
    transpose_state_changed = qt_compat.Signal(int)

    def __init__(self, model, parent=None):
        super(TableSourceWidgetXLS, self).__init__(parent)

        self._init_gui(model)

    def _init_gui(self, model):
        layout = QtGui.QVBoxLayout()

        # Worksheet Combobox
        self._worksheet_combobox = model.worksheet_name.gui()
        self._worksheet_combobox.setFixedWidth(200)
        layout.addWidget(self._worksheet_combobox)
        self._worksheet_combobox.editor().currentIndexChanged[int].connect(
            self.worksheet_changed)

        # Transpose checkbox
        self._transposed_checkbox = model.transposed.gui()
        layout.addWidget(self._transposed_checkbox)
        self._transposed_checkbox.stateChanged[int].connect(
            self.transpose_state_changed)

        self.setLayout(layout)
