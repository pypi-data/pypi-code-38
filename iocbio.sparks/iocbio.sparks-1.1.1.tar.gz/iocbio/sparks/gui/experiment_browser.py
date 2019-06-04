# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  Copyright (C) 2018
#   Laboratory of Systems Biology, Department of Cybernetics,
#   School of Science, Tallinn University of Technology
#  Authors: Martin Laasmaa and Marko Vendelin
#  This file is part of project: IOCBIO Sparks
#
import os
from PyQt5.QtCore import Qt, pyqtSignal, QSettings, QByteArray
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QCheckBox, QStackedLayout
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView, QMessageBox, QRadioButton, QGridLayout, QLineEdit

from collections import OrderedDict

from iocbio.sparks.constants import application_name
from iocbio.sparks.io.db import DatabaseInterface
from .custom_widgets import SmallLabel
from ..handler.experiment import ExperimentHandler
from ..io.export import export_experiments


class ExperimentBrowser(QTableWidget):
    """Class for displaying experiments in sqlite database"""

    sigRecordsSelected = pyqtSignal(list, list, bool)

    def __init__(self, database, database_table, data_to_fetch, record_to_show, multiselect=False):
        QTableWidget.__init__(self)

        self.database = database
        self.database_table = database_table
        self.data_to_fetch = data_to_fetch
        self.record_to_show = record_to_show
        self.multiselect = multiselect
        self.itemPressed.connect(self.experiment_selected)

        if not self.multiselect:
            self.itemDoubleClicked.connect(self.double_clicked)

        self.setSortingEnabled(True)
        self.prepare_table()
        self.set_data()

    def prepare_table(self):
        self.clear()
        self.setColumnCount(len(self.record_to_show))
        self.setRowCount(0)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(True)
        self.setHorizontalHeaderLabels(self.record_to_show)
        if not self.multiselect:
            self.setSelectionBehavior(QAbstractItemView.SelectItems)
            self.setSelectionMode(QAbstractItemView.SingleSelection)
        else:
            self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.horizontalHeader().setStretchLastSection(True)

    def set_data(self, clear_all=False):
        if clear_all:
            self.prepare_table()

        for experiment in self.database.query("SELECT %s FROM %s ORDER BY filename,comment" % (self.data_to_fetch,
                                                                                               self.database.table(self.database_table))):
            i = self.rowCount()
            self.insertRow(i)

            for j, key in enumerate(self.record_to_show):
                el = str(experiment[key])
                if key == 'transposed':
                    el = 'Yes' if el == '1' else 'No'
                item = QTableWidgetItem(el)
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                if j == 0:
                    item.experiment_id = experiment['experiment_id']
                self.setItem(i, j, item)

        self.resizeColumnsToContents()

    def double_clicked(self, item):
        if not self.multiselect:
            self.experiment_selected(item, True)
        else:
            return

    def keyPressEvent(self, event):
        if not self.multiselect and event.key() == Qt.Key_Return:
            self.experiment_selected(self.currentItem(), True)
        else:
            QTableWidget.keyPressEvent(self, event)

    def experiment_selected(self, item, excecute=False):
        row = item.row()

        if not self.multiselect:
            self.setCurrentCell(row, 0)

        selected_rows = []
        for item in self.selectedItems():
            row = item.row()
            if row not in selected_rows:
                selected_rows.append(row)

        l = []
        eid = []
        j = self.record_to_show.index('filename')
        for i in selected_rows:
            item = self.item(i, j)
            l.append(item.text())
            eid.append(item.experiment_id)

        self.sigRecordsSelected.emit(l, eid, excecute)


class OpenExperiment(QWidget):
    """Class for opening experiment that is in sqlite database"""
    settingGeometry = "Open Experiment GUI/geometry"
    settingReadOnly = "Open Experiment GUI/readonly"
    settingLastLoadPath = "Open Experiment GUI/last load directory"

    def __init__(self, database):
        QWidget.__init__(self)

        self.filename = None
        self.eid = None
        self.file_open_canceled = True
        self.connect_to_new_db = False
        self.database = database
        self.export_experiment_browser = None

        database_table = 'experiment_extended'
        data_to_fetch = 'experiment_id, filename, transposed, comment, spark_count'
        record_to_show = ['filename', 'transposed', 'comment', 'spark_count']

        self.experiment_table = ExperimentBrowser(database, database_table, data_to_fetch, record_to_show)
        self.experiment_table.sigRecordsSelected.connect(self.set_filename)
        open_from_file_btn = QPushButton('Open experiment file')
        export_db_btn = QPushButton('Export experiment(s)')
        connect_db_btn = QPushButton('Connect to database')
        open_from_db_btn = QPushButton('Open database experiment')
        rm_from_db_btn = QPushButton(' Remove experiment from database ')
        read_only_checkbox = QCheckBox('Read only mode. Note: When read-only, no changes will be saved')

        open_from_file_btn.clicked.connect(self.on_open_from_file_btn)
        export_db_btn.clicked.connect(self.on_export_db_btn)
        connect_db_btn.clicked.connect(self.on_connect_db)
        open_from_db_btn.clicked.connect(self.on_open_from_db_btn)
        rm_from_db_btn.clicked.connect(self.on_remove_from_db)
        read_only_checkbox.stateChanged.connect(lambda: self.set_database_read_only(read_only_checkbox.isChecked()))

        open_layout = QVBoxLayout()
        open_layout.addWidget(open_from_file_btn, 0, Qt.AlignLeft)
        open_layout.addWidget(QLabel('<b>or</b>'))
        open_layout.addWidget(QLabel('Select experiment from database:'))

        export_layout = QVBoxLayout()
        export_layout.addWidget(export_db_btn, 0, Qt.AlignLeft)
        export_layout.addWidget(SmallLabel('Export experiments to *.xlsx'), 0, Qt.AlignTop)

        connection_layout = QVBoxLayout()
        connection_layout.addWidget(connect_db_btn)

        for name, value in database.connection_parameters.items():
            connection_layout.addWidget(QLabel('%s: %s' % (name, value)))

        header_layout = QHBoxLayout()
        header_layout.addLayout(open_layout, 1)
        header_layout.addLayout(export_layout, 1)
        header_layout.addLayout(connection_layout, 0)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(open_from_db_btn, 1)
        btn_layout.addWidget(rm_from_db_btn, 0)

        layout = QVBoxLayout()
        layout.addLayout(header_layout)
        layout.addWidget(self.experiment_table)
        layout.addLayout(btn_layout)
        layout.addWidget(read_only_checkbox)
        self.setWindowTitle(application_name + ': open an experiment')
        self.setLayout(layout)

        # load settings
        settings = QSettings()
        self.restoreGeometry(settings.value(OpenExperiment.settingGeometry, QByteArray()))
        read_only_checkbox.setChecked(int(settings.value(OpenExperiment.settingReadOnly, 0)) > 0)
        self.last_load_path = settings.value(OpenExperiment.settingLastLoadPath, os.path.expanduser('~'))

    def on_open_from_file_btn(self):
        fname, ftype = QFileDialog.getOpenFileName(self,
                                                   caption='Open file',
                                                   directory=self.last_load_path,
                                                   filter='*.lsm;;(*.tiff *.tif);;All files (*)')
        if fname != '':
            self.file_open_canceled = False
            self.filename = fname
            self.last_load_path = os.path.dirname(self.filename)
            self.close()

    def on_open_from_db_btn(self):
        if self.filename is not None:
            self.file_open_canceled = False
            self.close()
        return

    def on_export_db_btn(self):
        self.export_experiment_browser = ExportExperiment(self.database)
        self.export_experiment_browser.sigWindowClosed.connect(self.disable_widget)
        self.export_experiment_browser.sigExportRequest.connect(export_experiments)
        self.export_experiment_browser.show()
        self.disable_widget(False)

    def disable_widget(self, b):
        self.setDisabled(not b)

    def on_connect_db(self):
        self.connect_to_new_db = True
        self.close()

    def on_remove_from_db(self):
        if self.eid is not None:
            ret = QMessageBox.warning(self, self.tr(application_name),
                                      self.tr('Following experiment will be removed from database:\n\n%s' % self.filename),
                                      QMessageBox.Cancel | QMessageBox.Ok,
                                      QMessageBox.Cancel)

            if ret == QMessageBox.Ok:
                ExperimentHandler.delete(self.database, self.eid)
                self.experiment_table.set_data(clear_all=True)

    def set_database_read_only(self, state):
        self.database.set_read_only(state)

    def set_filename(self, l, eid, excecute):
        'l is a list'
        self.filename = l[0]
        self.eid = eid[0]
        if excecute:
            self.file_open_canceled = False
            self.close()

    def closeEvent(self, event):
        settings = QSettings()
        settings.setValue(OpenExperiment.settingGeometry, self.saveGeometry())
        ro = 1 if self.database.read_only else 0
        settings.setValue(OpenExperiment.settingReadOnly, ro)
        settings.setValue(OpenExperiment.settingLastLoadPath, self.last_load_path)
        if self.file_open_canceled:
            self.filename = None

        self.close()
        event.accept()


class ExportExperiment(QWidget):
    """Class for exporting experiment that is in sqlite database"""
    settingGeometry = "Export Experiment GUI/geometry"
    settingLastSavePath = "Export Experiment GUI/last save directory"
    sigExportRequest = pyqtSignal(list, object, str, str)
    sigWindowClosed = pyqtSignal(bool)

    def __init__(self, database):
        QWidget.__init__(self)

        self.database = database
        self.filenames = []
        self.out_put_filename = ''
        self.out_put_filetype = '*.xlsx'

        database_table = 'experiment_extended'
        data_to_fetch = 'experiment_id, filename, comment, spark_count'
        record_to_show = ['filename', 'comment', 'spark_count']

        self.experiment_table = ExperimentBrowser(self.database, database_table, data_to_fetch, record_to_show, multiselect=True)
        self.experiment_table.sigRecordsSelected.connect(self.set_filename)
        export_experiments_btn = QPushButton('Export selected experiment(s)')

        export_experiments_btn.clicked.connect(self.export_experiments)

        layout = QVBoxLayout()
        layout.addWidget(QLabel('Select experiment from database:'))
        layout.addWidget(self.experiment_table)
        layout.addWidget(export_experiments_btn)
        self.setWindowTitle(application_name + ': export experiments')
        self.setLayout(layout)

        # load settings
        settings = QSettings()
        self.restoreGeometry(settings.value(ExportExperiment.settingGeometry, QByteArray()))
        self.last_save_path = settings.value(ExportExperiment.settingLastSavePath, os.path.expanduser('~'))

    def set_filename(self, l, eid, excecute):
        ''' l is a list '''
        self.filenames = l

    def update_expeiment_table(self):
        self.experiment_table.set_data(True)

    def export_experiments(self):
        self.out_put_filename, self.out_put_filetype = QFileDialog.getSaveFileName(self,
                                                                                   caption='Save file',
                                                                                   directory=self.last_save_path,
                                                                                   filter=self.out_put_filetype)
        if self.filenames != [] and self.out_put_filename != '':
            if not self.out_put_filename.endswith('.xlsx'):
                self.out_put_filename += '.xlsx'
            self.last_save_path = os.path.dirname(self.out_put_filename)
            self.sigExportRequest.emit(self.filenames, self.database, self.out_put_filename, self.out_put_filetype)
            self.close()

    def closeEvent(self, event):
        settings = QSettings()
        settings.setValue(ExportExperiment.settingGeometry, self.saveGeometry())
        settings.setValue(ExportExperiment.settingLastSavePath, self.last_save_path)
        self.close()
        self.sigWindowClosed.emit(True)
        event.accept()


class ConnectionParameters(QWidget):

    def __init__(self, parameters):
        QWidget.__init__(self)

        self.parameters = parameters
        layout = QGridLayout()
        for k, v in self.parameters.items():

            input_widget = QLineEdit(v['default'])
            input_widget.setMinimumWidth(150)
            v['field'] = input_widget

            row = layout.rowCount()
            layout.addWidget(QLabel(v['short']), row, 0)
            layout.addWidget(input_widget, row, 1)
            layout.addWidget(SmallLabel(v['description']), row+1, 0, 1, 2)
            layout.addWidget(SmallLabel(''), row+2, 0, 1, 2)

        self.setLayout(layout)

    def get_parameter_values(self):
        d = {}
        for k, v in self.parameters.items():
            d[k] = v['field'].text()
        return d


class ConnectDatabaseGUI(QWidget):
    """Class for selecting database type"""
    settingGeometry = "Connect Database GUI/geometry"

    def __init__(self):
        QWidget.__init__(self)

        settings = QSettings()
        dbtype = str(settings.value(DatabaseInterface.settings_dbtype, "sqlite3"))
        self.save_settings = False
        self.sqlite3 = QRadioButton('SQLite')
        self.postgresql = QRadioButton('PostgreSQL')
        getattr(self, dbtype).setChecked(True)
        connect = QPushButton('Connect')

        self.sqlite3.toggled.connect(self.show_dbtype_options)
        connect.clicked.connect(self.connect_database)

        psql_parameters = OrderedDict([
            ['hostname', {'short': 'Hostname', 'description': 'Hostname of database server', 'default': ''}],
            ['database', {'short': 'Database name', 'description': '', 'default': ''}],
            ['schema', {'short': 'Schema', 'description': 'PostgreSQL schema. For example: public', 'default': 'public'}],
            ])

        for key, value in psql_parameters.items():
            value['default'] = str(settings.value(getattr(DatabaseInterface, 'settings_pg_'+key), ''))

        self.layout_stack = QStackedLayout()
        self.sqlite_connection_parameters = QWidget()
        self.psql_connection_parameters = ConnectionParameters(psql_parameters)
        self.layout_stack.addWidget(self.sqlite_connection_parameters)
        self.layout_stack.addWidget(self.psql_connection_parameters)

        layout = QVBoxLayout()
        layout.addWidget(QLabel('Select database type:'))
        layout.addWidget(self.sqlite3)
        layout.addWidget(self.postgresql)
        layout.addLayout(self.layout_stack)
        layout.addStretch(1)
        layout.addWidget(connect)

        self.setWindowTitle(application_name + ': connect to database')
        self.setLayout(layout)
        self.show_dbtype_options()

        # load settings
        settings = QSettings()
        self.restoreGeometry(settings.value(ConnectDatabaseGUI.settingGeometry, QByteArray()))

    def show_dbtype_options(self):
        if self.sqlite3.isChecked():
            self.layout_stack.setCurrentWidget(self.sqlite_connection_parameters)
        if self.postgresql.isChecked():
            self.layout_stack.setCurrentWidget(self.psql_connection_parameters)

    def connect_database(self):
        settings = QSettings()
        settings.setValue(ConnectDatabaseGUI.settingGeometry, self.saveGeometry())
        if self.sqlite3.isChecked():
            settings.setValue(DatabaseInterface.settings_dbtype, 'sqlite3')
        if self.postgresql.isChecked():
            settings.setValue(DatabaseInterface.settings_dbtype, 'postgresql')
            for k, v in self.layout_stack.currentWidget().get_parameter_values().items():
                settings.setValue(getattr(DatabaseInterface, 'settings_pg_'+k), v)
        self.save_settings = True
        self.close()
