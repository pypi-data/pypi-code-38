# Copyright (c) 2018 Combine Control Systems AB
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
Imports a TDMS file into an ADAF. Each TDMS can contain an unlimited amount of
groups, where each groups holds a set of properties and an unlimited number of
channels (signal data).

The group properties will be stored in the ADAF's Meta section.

The raster is constructed from the fields wf_start_time, wf_increment, and
wf_start_offset, which are guaranteed to exist for each channel. The raster
will be in either datetime or float format, depending on the format of the
mentioned fields. If there isn't enough data to create a raster, an index
vector will be used.  The properties for each channel will be stored as column
attributes for the corresponding signal in the raster.
"""
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import nptdms
import os
import numpy as np
import datetime as dt
import itertools
from sympathy.api import importers
from sympathy.api import table


class DataImporterTDMS(importers.ADAFDataImporterBase):
    IMPORTER_NAME = "TDMS"

    def valid_for_file(self):
        if self._fq_infilename is None or not os.path.isfile(
                self._fq_infilename):
            return False
        with open(self._fq_infilename, 'rb') as f:
            return f.read(4) == b'TDSm'

    def import_data(self, out_adaf, parameters=None, progress=None):
        tdms = nptdms.TdmsFile(self._fq_infilename)
        meta_groups = []
        meta_dicts = []

        def channel_info(channel):
            properties = dict(channel.properties)
            start = properties.get('wf_start_time', 0)
            step = properties.get('wf_increment', 0)
            offs = properties.get('wf_start_offset', 0)
            channel_len = len(channel.data)
            return (start, step, offs, channel_len)

        out_sys = out_adaf.sys.create('TDMS')
        basis_properties = set(['wf_start_time', 'wf_increment',
                                'wf_start_offset',
                                'wf_samples'])

        for group in tdms.groups():
            meta_dict = dict(tdms.object(group).properties)
            if meta_dict:
                meta_groups.append(group)
                meta_dicts.append(meta_dict)

            rasters = {}
            n_rasters = len({channel_info(channel) for channel in
                             tdms.group_channels(group)})
            cnt = itertools.count()
            for channel in tdms.group_channels(group):
                # And each channel a raster starting at wf_start_time.
                properties = dict(channel.properties)
                info = channel_info(channel)
                start, step, offs, channel_len = info
                raster = rasters.get(info)

                if raster is None:
                    raster_name = group
                    if n_rasters > 1:
                        raster_name = '{} {}'.format(group, next(cnt))
                    raster = out_sys.create(raster_name)
                    rasters[info] = raster

                    if step == 0:
                        # No time basis can be created, use an index vector
                        tb = np.arange(channel_len)
                    elif isinstance(start, dt.datetime):
                        tb = np.array(
                            [start + dt.timedelta(seconds=offs + i * step)
                             for i in range(channel_len)])
                        properties['wf_start_time'] = start.isoformat()
                    else:
                        tb = np.arange(start + offs, channel_len,
                                       step=step or 1)

                    raster.create_basis(tb, attributes={
                        k: v for k, v in properties.items()
                        if k in basis_properties})

                raster.create_signal(
                    channel.channel, channel.data,
                    {k: v for k, v in properties.items()
                     if k not in basis_properties})
        if len(meta_groups):
            meta_table = table.File()
            for meta_group, meta_dict in zip(meta_groups, meta_dicts):
                for k, v in meta_dict.items():
                    meta_table['TDMS_{}_{}'.format(meta_group, k)] = (
                        np.array([v]))
            out_adaf.meta.from_table(meta_table)
