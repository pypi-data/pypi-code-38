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
import six
import sys
import os
import datetime
import json
import zipfile
from collections import OrderedDict
import numpy as np
import io

from sympathy.api import parameters as syparameters
from sympathy.api import importers
from sympathy.api import node as synode
from sympathy.api import adaf
from sympathy.api.exceptions import sywarn
from sympathy.api import qt as qt_compat
from sylib import mdflib
QtGui = qt_compat.import_module('QtGui')


def is_zipfile(filename):
    return (zipfile.is_zipfile(filename) &
            (os.path.splitext(filename)[-1] == u'.zip'))


def get_zip_buffer(filename, nbytes=-1, mode='r'):
    with zipfile.ZipFile(filename, mode) as mdfzip:
        clean_list = [
            elem for elem in mdfzip.namelist()
            if not (elem.startswith('.') | elem.startswith('_'))]

        filename_body = os.path.splitext(os.path.basename(filename))[0]

        if '{}.dat'.format(filename_body) in clean_list:
            file_to_import = '{}.dat'.format(filename_body)
        elif '{}.mdf'.format(filename_body) in clean_list:
            file_to_import = '{}.mdf'.format(filename_body)
        else:
            file_to_import = clean_list[0]

        with mdfzip.open(file_to_import, mode) as mdf_file:
            zip_buffer = io.BytesIO(mdf_file.read(nbytes))

    return zip_buffer


def ddecode(value, encoding):
    e = encoding
    if isinstance(value, dict):
        return {ddecode(k, e): ddecode(v, e) for k, v in value.items()}
    elif isinstance(value, list):
        return [ddecode(v, e) for v in value]
    elif isinstance(value, tuple):
        return [ddecode(v, e) for v in value]
    elif isinstance(value, six.binary_type):
        return value.decode(e)
    else:
        try:
            # Eliminate numpy types.
            return value.tolist()
        except AttributeError:
            return value


class DictWithoutNone(dict):
    """Dictionary which does not store None values."""
    def __init__(self, **kwargs):
        super(DictWithoutNone, self).__init__(
            **{key: value for key, value in kwargs.items()
               if value is not None})

    def __setitem__(self, key, value):
        if value is not None:
            super(DictWithoutNone, self).__setitem__(key, value)


def text_block(txblock, encoding):
    if txblock is not None:
        return txblock.get_text().rstrip().decode(encoding)


class MdfImporterWidget(QtGui.QWidget):
    def __init__(self, parameters, fq_infilename, *args, **kwargs):
        super(MdfImporterWidget, self).__init__(*args, **kwargs)
        self._parameters = syparameters(parameters)
        self._fq_infilename = fq_infilename
        self._init_gui()

    def _init_gui(self):
        encoding = self._parameters['encoding']
        default_file = self._parameters['default_file']
        allow_partial = self._parameters['partial']

        vlayout = QtGui.QVBoxLayout()
        vlayout.addWidget(encoding.gui())
        vlayout.addWidget(default_file.gui())
        vlayout.addWidget(allow_partial.gui())
        self.setLayout(vlayout)


class DataImporterMDF(importers.ADAFDataImporterBase):
    """Importer for an MDF file."""
    IMPORTER_NAME = "MDF"

    def __init__(self, fq_infilename, parameters):
        super(DataImporterMDF, self).__init__(fq_infilename, parameters)
        parameter_root = syparameters(parameters)
        if 'default_file' not in parameter_root:
            parameter_root.set_string(
                'default_file', value=u'',
                label='Default file:',
                editor=synode.Util.filename_editor().value())
        if 'encoding' not in parameter_root:
            parameter_root.set_string(
                'encoding', value=u'latin1',
                label='Character Encoding:',
                description='The name of a character encoding as '
                'recognized by python.')
        if 'partial' not in parameter_root:
            parameter_root.set_boolean(
                'partial', value=False,
                label='Import as much as possible from broken files',
                description=(
                    'Apply best effort to import as much as possible '
                    'from broken files instead of immediately failing the '
                    'import. In some cases, this allows reading partial data. '
                    'In other cases, the import may fail.'))

    def valid_for_file(self):
        if is_zipfile(self._fq_infilename):
            zip_buffer = get_zip_buffer(self._fq_infilename, 256)
            valid_file = mdflib.is_mdf(zip_buffer)
            zip_buffer.close()
        else:
            valid_file = mdflib.is_mdf(self._fq_infilename)

        return valid_file

    def parameter_view(self, parameters):
        return MdfImporterWidget(parameters, self._fq_infilename)

    def import_data(self, out_datafile, parameters=None, progress=None):
        parameter_root = syparameters(parameters)
        importer = MdfImporter(encoding=parameter_root['encoding'].value,
                               set_progress=progress or (lambda _: None),
                               allow_partial=parameter_root['partial'].value)
        temp_outfile = adaf.File()

        try:
            importer.run(self._fq_infilename, temp_outfile)
        except Exception:
            fq_default_filepath = parameter_root['default_file'].value
            message = u"Couldn't import file: {0}".format(self._fq_infilename)
            if fq_default_filepath:
                message += (u"\nFalling back to default file: {0}".format(
                    fq_default_filepath))
            sywarn(message)
            if fq_default_filepath:
                importer.run(fq_default_filepath, out_datafile)
            else:
                raise
        else:
            out_datafile.source(temp_outfile)


class MdfImporter(object):
    """Importer, back end for ImportMDF."""
    def __init__(self, encoding, set_progress, allow_partial):
        super(MdfImporter, self).__init__()

        self.system = None
        self.mdf = None
        self.reftime = None
        self.verbose = True
        self.encoding = encoding
        self.allow_partial = allow_partial

        if not set_progress:
            self.set_progress = lambda x: None
        else:
            self.set_progress = set_progress

    def run(self, fq_in_filename, out_datafile):
        """Process the data file."""
        self.set_progress(0)
        self.ddf = out_datafile

        if is_zipfile(fq_in_filename):
            file_object = get_zip_buffer(fq_in_filename)
            close_file = True
        else:
            file_object = fq_in_filename
            close_file = False

        with mdflib.MdfFile(file_object,
                            allow_partial=self.allow_partial) as self.mdf:
            # Set the test id as source identifier
            self.ddf.set_source_id(
                os.path.splitext(os.path.basename(fq_in_filename))[0])

            self._add_metadata(fq_in_filename)
            self._add_results(fq_in_filename)
            self._add_inca_system()
            self._add_timeseries()

        if close_file:
            file_object.close()

        self.set_progress(100)

    def _add_metadata(self, in_filename):
        """Add metadata to the data file."""
        # - File information
        # Filename
        data = os.path.basename(in_filename.split('\\')[-1])
        desc = 'MDF: filename of the mdf datafile'
        self.ddf.meta.create_column('MDF_filename', np.array([data]),
                                    {'description': desc})
        # Filename - fullpath
        data = in_filename
        desc = 'MDF: filename of the mdf datafile - fullpath'
        self.ddf.meta.create_column('MDF_filename_fullpath', np.array([data]),
                                    {'description': desc})

        # - Identification information
        # Program Identifier
        data = self.mdf.idblock.get_program_identifier()
        data = data.decode(self.encoding)
        desc = 'MDF: program that generated mdf file (measurement program)'
        self.ddf.meta.create_column('MDF_program', np.array([data]),
                                    {'description': desc})
        # Format Identifier
        data = self.mdf.idblock.version_number
        desc = 'MDF: version of MDF format'
        self.ddf.meta.create_column('MDF_version',
                                    np.array([six.text_type(data)]),
                                    {'description': desc})

        # - Header information
        # Date
        data = self.mdf.hdblock.date
        data = data.decode(self.encoding)
        date = data
        desc = 'MDF: Recording start date in "DD:MM:YYYY" format'
        self.ddf.meta.create_column('MDF_date', np.array([data]),
                                    {'description': desc})
        # Time
        data = self.mdf.hdblock.time
        data = data.decode(self.encoding)
        time = data
        desc = 'MDF: Recording start time in "HH:MM:SS" format'
        self.ddf.meta.create_column('MDF_time', np.array([data]),
                                    {'description': desc})

        self.reftime = datetime.datetime.strptime(
            '{} {}'.format(date, time), '%d:%m:%Y %H:%M:%S')

        desc = 'MDF: Recording start time'
        self.ddf.meta.create_column('MDF_datetime', np.array([self.reftime]),
                                    {'description': desc})

        # Author
        data = self.mdf.hdblock.get_author()
        data = data.decode(self.encoding)
        desc = 'MDF: Author name'
        self.ddf.meta.create_column('MDF_author', np.array([data]),
                                    {'description': desc})
        # Division
        data = self.mdf.hdblock.get_organization_or_department()
        data = data.decode(self.encoding)
        desc = 'MDF: Name of the organization or department'
        self.ddf.meta.create_column('MDF_division', np.array([data]),
                                    {'description': desc})
        # Project
        data = self.mdf.hdblock.get_project()
        data = data.decode(self.encoding)
        desc = 'MDF: Project name'
        self.ddf.meta.create_column('MDF_project', np.array([data]),
                                    {'description': desc})
        # Subject
        data = self.mdf.hdblock.get_subject_measurement_object()
        data = data.decode(self.encoding)
        desc = 'MDF: Subject / Measurement object, e.g. vehicle information'
        self.ddf.meta.create_column('MDF_subject', np.array([data]),
                                    {'description': desc})
        # Comment
        data = text_block(
            self.mdf.hdblock.get_file_comment(),
            self.encoding)
        if data is not None:
            desc = 'MDF: User test comment text'
            self.ddf.meta.create_column('MDF_comment', np.array([data]),
                                        {'description': desc})

            comments = data.split('\r\n')
            comments = comments[1:]
            for userinput in comments:
                if ":" in userinput:
                    data = userinput.split(':')
                    dataname = (data[0].lstrip()).rstrip()
                    dataname = dataname.replace(' ', '_')
                    dataname = "MDF_%s" % (dataname)
                    datavalue = ':'.join(data[1:])
                    datavalue = datavalue.strip()
                    desc = 'MDF: parsed user comment text'
                    self.ddf.meta.create_column(dataname,
                                                np.array([datavalue]),
                                                {'description': desc})

    def _add_results(self, in_filename):
        """Add data to result datagroup."""
        # Filename
        data = in_filename.split('\\')[-1]
        self.ddf.res.create_column('ts_filename', np.array([data]),
                                   {'description': 'Imported MDF file'})

    def _add_inca_system(self):
        """Add inca system to the data file."""
        group = self.ddf.sys
        # Add a new TimeSeriesSystem to TimeSeriesGroup tb[1]
        self.system = group.create('INCA')

    def _add_timeseries(self):
        """Add timeseries and their timebasis to the data file."""
        rcounter = 0

        # Create helper progress function
        def set_partial_progress(i):
            return self.set_progress(
                100.0 * i / self.mdf.hdblock.number_of_data_groups)

        # Loop over datagroups
        for i, dgblock in enumerate(self.mdf.hdblock.get_data_group_blocks()):
            cdict = OrderedDict()
            dblock = None
            try:
                dblock = dgblock.get_data_block()
            except Exception as e:
                if self.allow_partial:
                    print('WARNING, failed importing data block due to: {}'
                          .format(str(e)), file=sys.stderr)
                else:
                    raise

            if not dblock:
                continue

            # Loop over channelgroup
            for cgblock in dgblock.get_channel_group_blocks():
                cdict = OrderedDict([(cnblock.get_signal_name(), cnblock)
                                     for cnblock in
                                     cgblock.get_channel_blocks()])
                clist = list(cdict.keys())

                bases = [cnblock for cnblock in cdict.values()
                         if (cnblock.channel_type ==
                             mdflib.Channel.Types.TIMECHANNEL)]

                # Check raster type
                if len(bases) != 1:
                    sywarn("The group should have exactly one TIMECHANNEL")
                else:
                    cnblock = bases[0]
                    # Remove basis from channel list.
                    clist.remove(cnblock.get_signal_name())

                    if not cnblock:
                        continue
                    # Sampling rate in ms
                    sampling_rate = cnblock.get_sampling_rate()
                    signaldata, signalattr = dblock.get_channel_signal(
                        cgblock, cnblock)
                    extra_attr = signalattr or {}

                    # Create time raster
                    rcounter += 1

                    if cnblock.conversion_formula != 0:
                        ccblock = cnblock.get_conversion_formula()
                        unit = ccblock.get_physical_unit()
                    else:
                        unit = b's'
                    unit = unit.decode(self.encoding)
                    # Add this raster to list of timerasters
                    raster = self.system.create(
                        'Group{COUNT}'.format(COUNT=rcounter))

                    signaldescription = cnblock.get_signal_description()
                    signaldescription = signaldescription.decode(self.encoding)

                    # Add basis to raster
                    txblock = cnblock.get_comment()
                    comment = (txblock.get_text().decode(self.encoding)
                               if txblock else None)

                    raster.create_basis(signaldata, DictWithoutNone(
                        unit=unit,
                        description=signaldescription,
                        sampling_rate=sampling_rate,
                        comment=comment,
                        **{key: json.dumps(value) for key, value in
                           extra_attr.items()}))

                    txblock = cgblock.get_comment_block()
                    comment = (txblock.get_text().decode(self.encoding)
                               if txblock else None)

                    if comment:
                        raster.attr.set('comment', comment)

                    if self.reftime:
                        raster.attr.set('reference_time', self.reftime)

                    # Loop over channels
                    for cname in clist:

                        # Ignore channels with empty name
                        if not cname:
                            sywarn('Ignoring channel with empty name')
                            continue

                        # Get channel and extract needed information
                        cnblock = cdict[cname]

                        # Replace problematic character: /
                        signaldata, signalattr = dblock.get_channel_signal(
                            cgblock, cnblock)
                        if signaldata.dtype.kind == 'S':
                            try:
                                signaldata = np.char.decode(
                                    signaldata, self.encoding)
                            except UnicodeDecodeError:
                                pass
                        extra_attr = signalattr or {}
                        desc = cnblock.get_signal_description()
                        desc = desc.decode(self.encoding)
                        if cnblock.conversion_formula != 0:
                            ccblock = cnblock.get_conversion_formula()
                            unit = ccblock.get_physical_unit()
                        else:
                            unit = b'Unknown'
                        unit = unit.decode(self.encoding)
                        cname = cname.decode(self.encoding)
                        cname = cname.replace('/', '#')

                        txblock = cnblock.get_comment()
                        comment = (txblock.get_text().rstrip().decode(
                            self.encoding) if txblock else None)

                        extra_attr = {key: json.dumps(value)
                                      for key, value in
                                      ddecode(list(extra_attr.items()),
                                              self.encoding)}

                        raster.create_signal(
                            cname,
                            signaldata, DictWithoutNone(
                                unit=unit,
                                description=desc,
                                sampling_rate=sampling_rate,
                                comment=comment,
                                **extra_attr))

            set_partial_progress(i)

        # HACK(alexander): If exist, move active calibration page to result
        try:
            # Safest way if names are changed
            acp_name = self.ddf.ts.keys_fnmatch('*ActiveCalibration*')[0]
            # Get first sample
            acp_0 = self.ddf.ts[acp_name][:][0]
            self.ddf.res.create_column(
                'ActiveCalibrationPage', [acp_0],
                {'description': 'First sample from ActiveCalibrationPage'})
        except Exception:
            pass
