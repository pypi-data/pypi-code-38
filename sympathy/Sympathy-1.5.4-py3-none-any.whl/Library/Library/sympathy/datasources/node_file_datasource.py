# Copyright (c) 2013, 2017, Combine Control Systems AB
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
In Sympathy for Data, the action of pointing out where data is located and
actual import of data are separated into two different categories of
nodes. The internal data type Datasource is used to carry the information
about the location of the data to the import nodes.

There exist two nodes for establishing paths to locations with data, either
you are interested in a single source of data, :ref:`Datasource`, or several
sources, :ref:`Datasources`. The single source can either be a data file or a
location in a data base. While for multiple sources only several data files
are handled.
"""
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import os
from collections import OrderedDict
import six

from sympathy.common import filename_retriever_gui
from sympathy.api import node as synode
from sympathy.api import datasource as dsrc
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sympathy.api import qt as qt_compat
QtCore = qt_compat.QtCore
QtGui = qt_compat.import_module('QtGui')

MAX_DISPLAYED_FILES = 500
TIME_EXCEEDED_MSG = (
    'Preview took too long \n'
    '(no or few matches found in reasonable time).\n'
    '\nPlease execute the node to get all results.')


class SuperNode(object):
    author = "Alexander Busck <alexander.busck@combine.se>"
    copyright = "(C) 2013 Combine Control Systems AB"
    version = '1.1'
    icon = 'datasource.svg'
    tags = Tags(Tag.Input.Import)


class FileDatasourceWidget(QtGui.QWidget):
    def __init__(self, synode_context, parameters, parent=None):
        super(FileDatasourceWidget, self).__init__(parent)
        self._parameters = parameters

        self._init_gui()
        self._init_gui_from_parameters()

    def _init_gui(self):
        vlayout = QtGui.QVBoxLayout()
        vlayout.setContentsMargins(0, 0, 0, 0)

        file_widget = QtGui.QWidget()
        file_vlayout = QtGui.QVBoxLayout()
        file_widget.setLayout(file_vlayout)

        db_widget = QtGui.QWidget()
        db_vlayout = QtGui.QVBoxLayout()
        odbc_vlayout = QtGui.QVBoxLayout()
        sqlalchemy_vlayout = QtGui.QVBoxLayout()
        db_widget.setLayout(db_vlayout)

        self._filename_widget = self._parameters['filename'].gui()

        self._db_driver = self._parameters['db_driver']
        self._db_servername = self._parameters['db_servername']
        self._db_databasename = self._parameters['db_databasename']
        self._db_user = self._parameters['db_user']
        self._db_password = self._parameters['db_password']

        self._db_driver_widget = self._db_driver.gui()
        self._db_servername_widget = self._db_servername.gui()
        self._db_databasename_widget = self._db_databasename.gui()
        self._db_user_widget = self._db_user.gui()
        self._db_password_widget = self._db_password.gui()

        self._connection_widget = (
            self._parameters['db_connection_string'].gui())
        self._db_sqlalchemy_engine_url = (
            self._parameters['db_sqlalchemy_engine_url'].gui())
        self._db_method = (
            self._parameters['db_method'].gui())

        self._type_selector = QtGui.QComboBox()
        self._type_selector.addItem('File')
        self._type_selector.addItem('Database')
        self._type_selector.setCurrentIndex(
            self._parameters['datasource_type'].value[0])
        self._datasource_stackwidget = QtGui.QStackedWidget()

        file_vlayout.addWidget(self._filename_widget)

        self._odbc_split_widgets = [
            self._db_driver_widget,
            self._db_servername_widget,
            self._db_databasename_widget,
            self._db_user_widget,
            self._db_password_widget]

        self._connection_widget_active = False

        file_vlayout.addStretch()

        self._sqlalchemy_group = QtGui.QGroupBox('SQLAlchemy settings')
        self._sqlalchemy_group.setLayout(sqlalchemy_vlayout)
        self._odbc_group = QtGui.QGroupBox('ODBC settings')
        self._odbc_group.setLayout(odbc_vlayout)

        self._db_methods = OrderedDict(
            zip(_db_options, [self._odbc_group, self._sqlalchemy_group]))

        for odbc_split_widget in self._odbc_split_widgets:
            odbc_vlayout.addWidget(odbc_split_widget)

        for odbc_split in [self._db_driver,
                           self._db_servername,
                           self._db_databasename,
                           self._db_user,
                           self._db_password]:
            odbc_split.value_changed.add_handler(self._odbc_split_changed)

        odbc_vlayout.addWidget(self._connection_widget)
        sqlalchemy_vlayout.addWidget(self._db_sqlalchemy_engine_url)

        db_vlayout.addWidget(self._db_method)
        db_vlayout.addWidget(self._sqlalchemy_group)
        db_vlayout.addWidget(self._odbc_group)

        self._datasource_stackwidget.addWidget(file_widget)
        self._datasource_stackwidget.addWidget(db_widget)

        vlayout.addWidget(self._type_selector)
        vlayout.addWidget(self._datasource_stackwidget)

        self.setLayout(vlayout)

        self._type_selector.currentIndexChanged[int].connect(
            self._type_changed)

        self._db_method_changed(self._parameters['db_method'].value)
        self._db_method.valueChanged.connect(
            self._db_method_changed)

    def _init_gui_from_parameters(self):
        try:
            index = self._parameters['datasource_type'].value[0]
        except KeyError:
            index = 0
        self._datasource_stackwidget.setCurrentIndex(index)

    def _type_changed(self, index):
        self._parameters['datasource_type'].value = [index]
        self._datasource_stackwidget.setCurrentIndex(index)

    def _odbc_split_changed(self):
        args = [
            self._db_driver.selected,
            self._db_servername.value,
            self._db_databasename.value,
            self._db_user.value,
            self._db_password.value]

        tabledata = dsrc.File.to_database_dict(*args, db_method='ODBC')
        self._connection_widget.set_value(tabledata['path'])

    def _db_method_changed(self, value):
        for key, db_method in self._db_methods.items():
            db_method.setEnabled(key == value)


def datasource_factory(datasource, parameter_root):
    try:
        datasource_type = parameter_root['datasource_type'].selected
    except KeyError:
        datasource_type = 'File'

    if datasource_type == 'File':
        tabledata = datasource.to_file_dict(
            os.path.abspath(parameter_root['filename'].value))
    elif datasource_type == 'Database':
        db_method = parameter_root['db_method'].value
        if db_method == 'ODBC':
            args = [
                parameter_root['db_driver'].selected,
                parameter_root['db_servername'].value,
                parameter_root['db_databasename'].value,
                parameter_root['db_user'].value,
                parameter_root['db_password'].value,
                parameter_root['db_connection_string'].value]
        elif db_method == 'SQLAlchemy':
            args = [
                parameter_root['db_sqlalchemy_engine_url'].value]

        tabledata = datasource.to_database_dict(*args, db_method=db_method)
    else:
        assert(False)

    return tabledata


_db_options = ['ODBC', 'SQLAlchemy']


class FileDatasource(SuperNode, synode.Node):
    """
    Create Datasource with path to a data source.

    :Ref. nodes: :ref:`Datasources`
    """

    name = 'Datasource'
    description = 'Select a data source.'
    nodeid = 'org.sysess.sympathy.datasources.filedatasource'

    outputs = Ports([Port.Datasource(
        'Datasource with path to file', name='port1', scheme='text')])

    parameters = synode.parameters()
    parameters.set_string(
        'filename', label='Filename',
        description='A filename including path if needed',
        editor=synode.Util.filename_editor(['Any files (*)']))
    parameters.set_string(
        'db_sqlalchemy_engine_url', label='SQLAlchemy engine URL',
        value='mssql+pyodbc:///',
        description='SQLAlchemy engine URL for connecting to the database')
    parameters.set_string(
        'db_method',
        label='Database connection method',
        editor=synode.Util.combo_editor(options=_db_options),
        value=_db_options[0],
        description=(
            'Select which Database connection method that you want to use.'))
    parameters.set_list(
        'db_driver', ['SQL Server'], label='Database driver',
        description='Database driver to use.',
        editor=synode.Util.combo_editor())
    parameters.set_string(
        'db_servername', label='Server name',
        description='A valid name to a database server.')
    parameters.set_string(
        'db_databasename', label='Database name',
        description='The name of the database.')
    parameters.set_string(
        'db_user', label='User',
        description='A valid database user.')
    parameters.set_string(
        'db_password', label='Password',
        description='A valid password for the selected user.')
    parameters.set_string(
        'db_connection_string', label='Connection string',
        description='A connection string that will override other settings.')

    parameters.set_list(
        'datasource_type', ['File', 'Database'], label='Datasource type',
        description='Type of datasource.')

    INTERACTIVE_NODE_ARGUMENTS = {
        'uri': ['filename', 'value']
    }

    def exec_parameter_view(self, synode_context):
        return FileDatasourceWidget(
            synode_context, synode_context.parameters)

    def execute(self, synode_context):
        """Execute"""
        synode_context.output['port1'].encode(
            datasource_factory(synode_context.output['port1'],
                               synode_context.parameters))


class FileDatasourcesWidget(QtGui.QWidget):
    def __init__(self, synode_context, parameter_root, parent=None):
        super(FileDatasourcesWidget, self).__init__(parent)
        self._parameter_root = parameter_root

        self._init_gui()

    def _init_gui(self):
        vlayout = QtGui.QVBoxLayout()
        vlayout.setContentsMargins(0, 0, 0, 0)

        use_recursive_widget = self._parameter_root['recursive'].gui()
        self._directory_widget = self._parameter_root['directory'].gui()
        search_pattern_widget = self._parameter_root['search_pattern'].gui()
        self._file_widget = QtGui.QListWidget()
        self._file_widget.setAlternatingRowColors(True)
        self._file_widget.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        _file_widget_label = QtGui.QLabel(
            'Preview ({} first hits displayed)'.format(MAX_DISPLAYED_FILES))

        vlayout.addWidget(use_recursive_widget)
        vlayout.addWidget(self._directory_widget)
        vlayout.addWidget(search_pattern_widget)
        vlayout.addWidget(_file_widget_label)
        vlayout.addWidget(self._file_widget)
        self.setLayout(vlayout)

        self._update_filewidget()

        use_recursive_widget.stateChanged.connect(
            self._update_filewidget)
        self._directory_widget.editor().dialogChanged[six.text_type].connect(
            self._update_filewidget)
        self._directory_widget.editor().text_changed.connect(
            self._update_filewidget)
        search_pattern_widget.valueChanged.connect(
            self._update_filewidget)

    def _update_filewidget(self):
        filename_retriever = filename_retriever_gui.FilenameRetriever(
            self._directory_widget.editor().filename(),
            self._parameter_root['search_pattern'].value)

        selected_fq_filenames = filename_retriever.filenames(
            fully_qualified=True,
            recursive=self._parameter_root['recursive'].value,
            max_length=MAX_DISPLAYED_FILES, max_length_msg=TIME_EXCEEDED_MSG)
        self._file_widget.clear()
        self._file_widget.addItems(selected_fq_filenames)


class FileDatasourceMultiple(SuperNode, synode.Node):
    """
    Create Datasources with paths to data sources.

    :Ref. nodes: :ref:`Datasource`
    """

    name = 'Datasources'
    description = 'Select data sources.'
    nodeid = 'org.sysess.sympathy.datasources.filedatasourcemultiple'

    outputs = Ports([Port.Datasources(
        'Datasources with paths files',
        name='port1', scheme='text')])

    parameters = synode.parameters()
    parameters.set_boolean(
        'recursive', value=False, label='Recursive',
        description=('If unchecked, only the selected directory will be '
                     'searched. If checked, all subdirectories of the '
                     'selected directory will also be searched.'))
    parameters.set_string(
        'directory', label='Directory',
        description=('Directory where to search for files.'),
        editor=synode.Util.directory_editor())
    parameters.set_string(
        'search_pattern', value='*', label='Search pattern',
        description='A wildcard pattern which the filenames must match.')

    def exec_parameter_view(self, synode_context):
        return FileDatasourcesWidget(synode_context, synode_context.parameters)

    def execute(self, synode_context):
        """Create a list of datasources and add them to the output
        file.
        """
        filename_retriever = filename_retriever_gui.FilenameRetriever(
            synode_context.parameters['directory'].value,
            synode_context.parameters['search_pattern'].value)

        selected_fq_filenames = filename_retriever.filenames(
            fully_qualified=True,
            recursive=synode_context.parameters['recursive'].value)

        for fq_filename in selected_fq_filenames:
            datasource = dsrc.File()
            datasource.encode_path(os.path.abspath(fq_filename))
            synode_context.output['port1'].append(datasource)
