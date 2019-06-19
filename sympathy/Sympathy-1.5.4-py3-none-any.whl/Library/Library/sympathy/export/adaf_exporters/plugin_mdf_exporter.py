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
import numpy as np
import six
import json

from sympathy.api import qt as qt_compat
from sympathy.api.exceptions import SyDataError
from sylib import mdflib
from sylib.export import adaf as exportadaf
QtGui = qt_compat.import_module('QtGui')


class DataExportMDFWidget(exportadaf.TabbedDataExportWidget):

    def _init_gui(self):
        vlayout = QtGui.QVBoxLayout()
        vlayout.setContentsMargins(0, 0, 0, 0)
        vlayout.addWidget(self._parameter_root['encoding'].gui())
        vlayout.addWidget(self._tabbed_strategy_widget)
        self.setLayout(vlayout)


class DataExportMDF(exportadaf.TabbedADAFDataExporterBase):
    """Exporter for MDF files."""
    EXPORTER_NAME = "MDF"
    FILENAME_EXTENSION = "dat"

    def __init__(self, parameters):
        super(DataExportMDF, self).__init__(parameters)
        if 'encoding' not in self._parameters:
            self._parameters.set_string(
                'encoding', u'latin1', label="Character encoding:",
                description="All strings in the adaf file will be encoded "
                "using this character encoding.")

    def parameter_view(self, input_list):
        return DataExportMDFWidget(self._parameters,
                                   input_list)

    def export_data(self, adafdata, fq_outfilename, progress):
        """Export ADAF to MDF."""
        exporter = MdfExporter(self._parameters['encoding'].value,
                               progress)
        exporter.run(adafdata, fq_outfilename)


class MdfExporter(object):
    """This class handles exporting of ADAF to MDF."""

    def __init__(self, encoding, set_progress=lambda x: None):
        self.set_progress = set_progress
        self.encoding = encoding

    def run(self, adafdata, fq_out_filename):
        """Process the MDF file."""

        self.set_progress(0.)
        self.adaf = adafdata

        with mdflib.MdfFile(fq_out_filename, 'w+b') as self.mdf:
            self.mdf.default_init()

            # TODO: This exporter currently doesn't export any results
            self._add_metadata()
            self.set_progress(10.)
            (self.mdf.hdblock.data_group_block,
             self.mdf.hdblock.number_of_data_groups) = self._add_timeseries()

            self.mdf.write()
            self.set_progress(100.)

    def _add_metadata(self):
        """Add metadata to the MDF file."""

        def from_meta(dataset):
            """Add metadata entry to the MDF file if it exists."""
            if dataset in self.adaf.meta.keys():
                data = self.adaf.meta[dataset]

                if data.size() > 0:
                    return data.value()[0]
            return None

        def unicode_from_meta(dataset):
            data = from_meta(dataset)
            if data is not None:
                if isinstance(data, six.text_type):
                    return data.encode(self.encoding)
            else:
                return None

        # ID information
        idblock = self.mdf.idblock
        # Program Identifier
        value = unicode_from_meta('MDF_program')
        if value is not None:
            idblock.program_identifier = value
        # Format Identifier
        value = from_meta('MDF_version')
        if value is not None:
            idblock.version_number = int(value)

        # HD information
        hdblock = self.mdf.hdblock
        # Date
        value = unicode_from_meta('MDF_date')
        if value is not None:
            hdblock.date = value
        # Time
        value = unicode_from_meta('MDF_time')
        if value is not None:
            hdblock.time = value
        # Author
        value = unicode_from_meta('MDF_author')
        if value is not None:
            hdblock.author = value
        # Division
        value = unicode_from_meta('MDF_division')
        if value is not None:
            hdblock.organization_or_department = value
        # Project
        value = unicode_from_meta('MDF_project')
        if value is not None:
            hdblock.project = value
        # Subject
        value = unicode_from_meta('MDF_subject')
        if value is not None:
            hdblock.subject_measurement_object = value
        # Comment
        value = unicode_from_meta('MDF_comment')
        if value is not None:
            hdblock.file_comment = self.mdf.write_text(value)

    def _add_timeseries(self):
        """Add timeseries to the MDF file."""

        try:
            return self.mdf.write_channel_groups(
                SystemsRasterIterator(
                    self.adaf.sys, self.set_progress, self.encoding))
        except mdflib.MdfError as me:
            raise SyDataError('MdfError: {}'.format(me))


class RasterColumnIterator(object):
    """
    RasterColumnIterator is an iterator over Columns in the Raster with the
    following properties:
        The elements are a tripple (data, unit, name) of types
        (ndarray, str, str)
        unit and name are encoded using provided encoding.
        Furthermore, __iter__, and reverse are provided to enable
        acting as a limited list.
    """
    def __init__(self, raster, encoding):
        self.raster = raster
        self.encoding = encoding
        self._reverse = False

    def reverse(self):
        self._reverse ^= True

    def __iter__(self):
        raster = self.raster
        reverse = self._reverse
        encoding = self.encoding
        keys = list(self.raster.keys())
        basis = (raster.basis_column().value(),
                 raster.basis_column().attr['unit'].encode(encoding),
                 raster.basis_column().attr['description'].encode(encoding),
                 None,
                 'time')

        if not reverse:
            yield basis
        else:
            keys.reverse()

        for name in keys:
            signal = raster[name]

            try:
                conv = json.loads(
                    signal.get_attributes()['conversion'])
                if 'conversion_type' not in conv:
                    conv = None
            except (KeyError, ValueError):
                conv = None

            signal_data = signal.y

            if signal_data.dtype.kind is 'U':
                signal_data = np.core.defchararray.encode(
                    signal_data, encoding)
            yield((signal_data,
                   signal.unit().encode(encoding),
                   signal.description().encode(encoding),
                   conv,
                   name.encode(encoding)))
        if reverse:
            yield basis


class SystemsRasterIterator(object):
    """
    SystemsRasterIterator is an iterator over Rasters in the Systems.
    After yielding optaining an element, progress is updated.
    The elements are a tripple (name, raster, sampling_rate) of types
    (str, RasterColumnIterator, float).
    """
    def __init__(self, systems_group, set_progress, encoding):
        self.systems_group = systems_group
        self.set_progress = set_progress
        self.encoding = encoding

    def __iter__(self):
        encoding = self.encoding
        system_count = len(self.systems_group.keys())
        for si, system_name in enumerate(self.systems_group.keys()):
            system = self.systems_group[system_name]
            raster_count = len(system.keys())

            for ri, raster_name in enumerate(reversed(system.keys())):
                raster = system[raster_name]
                # TODO: How to find the sampling rate if it exists? Is
                # it only used to name the raster or is it used in any
                # other way too?
                try:
                    sampling_rate = float(
                        raster.basis_column().attr['sampling_rate'])
                except KeyError:
                    sampling_rate = 0.0

                yield (raster_name.encode(encoding),
                       RasterColumnIterator(raster, encoding),
                       sampling_rate)
                self.set_progress(
                    100 * (float(si) + float(ri) / raster_count) /
                    system_count)
