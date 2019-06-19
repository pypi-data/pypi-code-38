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
ADAF is an internal data type in Sympathy for Data. In the ADAF different
kind of data, metadata (data about data), results (aggregated/calculated data)
and timeseries (accumulated time-resolved data), connected to a simultaneous
event can be stored together with defined connections to each other.

The different kinds of data are separated into containers. For the metadata
and the results, the containers consist of a set of signals stored as a
:ref:`Table`.

For the time-resolved data, the container has a more advanced structure.
The time-resolved data from a measurement can have been collected from
different measurement system and the data can, because of different reason,
not be stored together. For example, the two systems do not using the same
sample rate or do not have a common absolute zero time. The timeseries
container in the ADAF can therefore include one or many system containers.
Even within a measurement system, data can have been measured with different
sample rates, therefore the system container can consist of one or many
rasters. Each raster consists of a time base and a set of corresponding
signals, which all are stored as the internal :ref:`Table` type.

This node uses plugins. Each supported file format has its own plugin. The
plugins have their own configurations which are reached by choosing among the
importers in the configuration GUI. The documentation for each plugin is
obtained by clicking at listed file formats below.

The node has an auto configuration which uses a validity check in the plugins
to detect and choose the proper plugin for the considered datasource. When
the node is executed in the auto mode the default settings for the plugins
will be used.

"""
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
from sylib.importer import base
from sympathy.api import node as synode
from sympathy.api import importers
from sympathy.api.nodeconfig import Port, Ports


class ImportADAF(base.ImportSingle, synode.Node):
    """
    Import datasource as ADAF.

    :Configuration: See description for specific plugin
    :Opposite node: :ref:`Export ADAFs`
    :Ref. nodes: :ref:`ADAFs`

    For instructions on how to add or write custom plugins, see
    :ref:`pluginwriting`.
    """
    author = "Alexander Busck <alexander.busck@combine.se>"
    copyright = "(C) 2013 Combine Control Systems AB"
    version = '1.0'
    name = 'ADAF'
    description = 'Data source as ADAF'
    nodeid = 'org.sysess.sympathy.data.adaf.importadaf'
    icon = 'import_adaf.svg'
    outputs = Ports([Port.ADAF('Imported ADAF')])
    plugins = (importers.ADAFDataImporterBase, )


class ImportADAFs(base.ImportMulti, synode.Node):
    """
    Import file(s) into the platform as ADAF(s).

    :Opposite node: :ref:`Export ADAFs`
    :Ref. nodes: :ref:`ADAF`

    For instructions on how to add or write custom plugins, see
    :ref:`pluginwriting`.
    """
    author = "Alexander Busck <alexander.busck@combine.se>"
    copyright = "(C) 2013 Combine Control Systems AB"
    version = '1.0'
    name = 'ADAFs'
    description = 'Import multiple adaf files'
    nodeid = 'org.sysess.sympathy.data.adaf.importadafs'
    icon = 'import_adaf.svg'
    outputs = Ports([Port.ADAFs('Imported ADAFs', name='output')])
    plugins = (importers.ADAFDataImporterBase, )
