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
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import traceback
import six
from .. utils.components import get_components
from .. utils import context
from .. platform.exceptions import sywarn

from .. platform import qt_compat
QtGui = qt_compat.import_module(str('QtGui'))


class DATASOURCE(object):
    FILE = 'FILE'
    DATABASE = 'DATABASE'


class IDataImportFactory(object):
    """A factory interface for DataImporters."""
    def __init__(self):
        super(IDataImportFactory, self).__init__()

    def importer_from_datasource(self, datasource):
        """Get an importer from the given datasource."""
        raise NotImplementedError("Not implemented for interface.")


class IDataSniffer(object):
    def __init__(self):
        super(IDataSniffer, self).__init__()

    def sniff(self, path):
        """Sniff the given file and return the data format."""
        raise NotImplementedError("Not implemented for interface.")


class IDataImporterWidget(object):
    """Interface for data importer widgets, used to configure
    parameters to the importer."""
    def __init__(self):
        pass


class DataImporterLocator(object):
    """Given a folder locate all eligable importer classes derived from
    the IDataImporter interface."""
    def __init__(self, importer_parent_class):
        super(DataImporterLocator, self).__init__()
        self._importer_parent_class = importer_parent_class

    def importer_from_sniffer(self, file2import):
        """Use sniffers to evaluate a valid importer and return it."""
        def valid_importer(c):
            return c(file2import, None).valid_for_file()

        for importer in get_components('plugin_*.py',
                                       self._importer_parent_class):
            try:
                if valid_importer(importer):
                    return importer
            except Exception:
                sywarn("{} importer failed to sniff resource. "
                       "The exception was:\n{}".format(
                           importer.display_name(), traceback.format_exc()))

        return None

    def importer_from_name(self, importer_name):
        """Return the importer associated with importer_name."""
        importers = get_components('plugin_*.py', self._importer_parent_class)
        valid_importers = (importer for importer in importers
                           if importer.IMPORTER_NAME == importer_name)
        try:
            return six.next(valid_importers)
        except StopIteration:
            raise KeyError(importer_name)

    def available_importers(self, datasource_compatibility=None):
        """Return the available importers."""
        importers = get_components('plugin_*.py', self._importer_parent_class)
        if datasource_compatibility is None:
            return {importer.IMPORTER_NAME: importer for importer in importers}
        else:
            return {importer.IMPORTER_NAME: importer for importer in importers
                    if datasource_compatibility in importer.DATASOURCES}


class ImporterConfigurationWidget(QtGui.QWidget):
    def __init__(self, available_importers, parameters,
                 fq_infilename, parent=None):
        super(ImporterConfigurationWidget, self).__init__(parent)
        self._parameters = parameters
        self._custom_parameters = self._parameters["custom_importer_data"]
        self._available_importers = available_importers
        self._importer_name = None
        self._fq_infilename = fq_infilename
        self.widgets = []

        self._init_gui()
        self._init_gui_from_parameters()

    def _init_gui(self):
        vlayout = QtGui.QVBoxLayout()
        vlayout.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        hlayout = QtGui.QHBoxLayout()

        importer_label = QtGui.QLabel("Importer to use")
        self._importer_combobox = QtGui.QComboBox()
        hlayout.addWidget(importer_label)
        hlayout.addWidget(self._importer_combobox)
        hlayout.addSpacing(250)

        self.stacked_widget = QtGui.QStackedWidget()

        importers = sorted(
            self._available_importers.values(),
            key=lambda x: x.display_name())

        for i, importer_cls in enumerate(importers):
            self._importer_combobox.addItem(importer_cls.display_name())
            self._importer_combobox.setItemData(i, importer_cls.identifier())

        for importer_cls in importers:
            imp_name = importer_cls.identifier()
            disp_name = importer_cls.display_name()

            try:
                if imp_name not in self._custom_parameters:
                    self._custom_parameters.create_group(imp_name)

                importer = importer_cls(self._fq_infilename,
                                        self._custom_parameters[imp_name])

                if not getattr(importer.parameter_view, 'original', False):
                    parameter_widget = (
                        importer.parameter_view(
                            self._custom_parameters[imp_name]))
                else:
                    parameter_widget = QtGui.QLabel()

            except Exception:
                parameter_widget = QtGui.QLabel('Failed to load')
                sywarn("{} importer failed to build its configuration gui. "
                       "The exception was:\n{}".format(
                           disp_name, traceback.format_exc()))

            self.stacked_widget.addWidget(parameter_widget)
            self.widgets.append(parameter_widget)

        vlayout.addItem(hlayout)
        vlayout.addWidget(self.stacked_widget)
        vlayout.addItem(QtGui.QSpacerItem(500, 1))
        fail_layout = QtGui.QHBoxLayout()
        fail_layout.addWidget(self._parameters['fail_strategy'].gui())
        vlayout.addItem(fail_layout)
        self.setLayout(vlayout)

        self._importer_combobox.currentIndexChanged[int].connect(
            self._importer_changed)
        self._importer_combobox.activated.connect(
            self.stacked_widget.setCurrentIndex)

    def _init_gui_from_parameters(self):
        active_importer = self._parameters["active_importer"].value
        index = self._importer_combobox.findData(active_importer)
        # Select the first item if none is selected.
        if index == -1:
            self._importer_combobox.setCurrentIndex(0)
        else:
            self._importer_combobox.setCurrentIndex(index)

    def _importer_changed(self, index):
        active_importer = str(self._importer_combobox.itemData(index))
        self._parameters["active_importer"].value = active_importer
        self.stacked_widget.setCurrentIndex(index)

    def cleanup(self):
        for parameter_widget in self.widgets:
            if parameter_widget and hasattr(parameter_widget, 'cleanup'):
                parameter_widget.cleanup()


# External API

class IDataImporter(object):
    """Interface for a DataImporter. It's important to set IMPORTER_NAME
    to a unique name otherwise errors will occur."""
    IMPORTER_NAME = "UNDEFINED"
    DISPLAY_NAME = None
    DATASOURCES = [DATASOURCE.FILE]

    def __init__(self, fq_infilename, parameters):
        """
        Parameters
        ----------
        fq_infilename : six.text_type
                        Fully qualified filename.
        parameters : ParameterGroup or NoneType
                     plugin parameters or None, make sure to handle the case
                     where None is passed for parameters.
        """
        super(IDataImporter, self).__init__()
        self._fq_infilename = fq_infilename
        self._parameters = parameters

    @classmethod
    def identifier(cls):
        """
        Returns
        -------
        six.text_type
            Unique identifier for importer.
        """
        return cls.IMPORTER_NAME

    @classmethod
    def display_name(cls):
        """
        Returns
        -------
        six.text_type
            Display name for importer.
        """
        return cls.DISPLAY_NAME or cls.IMPORTER_NAME

    def valid_for_file(self):
        """
        Returns
        -------
        bool
            True if plugin handles self._fq_infilename.
        """
        return False

    def import_data(self, out_file, parameters=None, progress=None):
        """
        Fill out_file with data.
        """
        raise NotImplementedError

    @classmethod
    def name(cls):
        """
        Returns
        -------
        six.text_type
            Name for importer.
        """
        return cls.IMPORTER_NAME

    @context.original
    def parameter_view(self, parameters):
        """
        Returns
        -------
        QtGui.QWidget
            GUI widget for importer.
        """
        return QtGui.QWidget()

    def is_type(self):
        """
        Returns
        -------
        bool
            True if self._fq_infilename points to a native "sydata file.
        """
        return False


class ADAFDataImporterBase(IDataImporter):
    def __init__(self, fq_infilename, parameters):
        super(ADAFDataImporterBase, self).__init__(fq_infilename, parameters)

    def valid_for_file(self):
        """Return True if this importer is valid for fq_filename."""
        return False

    def is_type(self):
        return self.is_adaf()

    def is_adaf(self):
        """Is the file to be imported a valid ADAF file."""
        return False


class TableDataImporterBase(IDataImporter):
    def __init__(self, fq_infilename, parameters):
        super(TableDataImporterBase, self).__init__(fq_infilename, parameters)

    def valid_for_file(self):
        """Return True if this importer is valid for fq_filename."""
        return False

    def is_type(self):
        return self.is_table()

    def is_table(self):
        """Is the file to be imported a valid Table file."""
        return False


class TextDataImporterBase(IDataImporter):
    def __init__(self, fq_infilename, parameters):
        super(TextDataImporterBase, self).__init__(fq_infilename, parameters)

    def valid_for_file(self):
        """Return True if this importer is valid for fq_filename."""
        return False

    def is_type(self):
        return self.is_text()

    def is_text(self):
        """Is the file to be imported a valid Table file."""
        return False


def available_plugins(plugin_base_class, datasource_compatibility=None):
    dil = DataImporterLocator(plugin_base_class)
    return dil.available_importers(datasource_compatibility)


def plugin_for_file(plugin_base_class, filename):
    dil = DataImporterLocator(plugin_base_class)
    return dil.importer_from_sniffer(filename)


def configuration_widget(plugins, parameters, filename):
    return ImporterConfigurationWidget(plugins, parameters, filename)
