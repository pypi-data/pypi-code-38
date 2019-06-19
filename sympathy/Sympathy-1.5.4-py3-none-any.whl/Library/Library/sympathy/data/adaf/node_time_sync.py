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
With the :ref:`ADAF` format it is possible to store data from an experiment
that has been simultaneously measured by different measurement systems. This
possibility raises the oppportunity to perform cross analysis between
quantities gathered by the different systems. Common sitaution, and problem,
is that there may not exist a mutual absolute zero time between the systems.
A time synchronization may therefore be a necessity in order to have correlated
timebases which is required for cross analysis.

The synchronization process requires that two systems are specified, where one
of them is defined to be the reference system. An offset between the systems
will be calculated by using one of the following methods:

- OptimizationLSF
- Shared event (positive)
- Shared event (negative)
- Sync parts

This offset is then used to shift the timebases in the non-reference ("syncee")
system. To obtain the offset it is important that there is a synchronization
signal in both of the systems. The signals should be of the same quantity and
have the same unit.

*Shared event*
  When using any of the shared event strategies a specified threshold in the
  synchronization signal determines the shared event that is used to calculate
  the offset with the above mentioned methods. *Positive* or *negative* in the
  name of the strategy refers to what value the derivative of the signal should
  have. Positive means that the signal should rise above the threshold to
  qualify as a shared event, whereas negative means that the signal should drop
  below the threshold.

*OptimizationLSF*
  This strategy starts off with a shared event (positive) strategy for finding
  a starting guess. After that it chooses 500 randomly distributed points and
  does a least square fit of the two signals evaluated in those randomly
  distributed points. This means that minor random variations can occur when
  using this strategy.

*Sync parts*
  If you want to do many-to-one syncronization you should use *Sync parts*. The
  system with one long meassurement should be chosen as reference system. The
  other system can have many shorter parts which should be vjoined beforehand
  (:ref:`VJoin ADAFs`). Choose the Vjoin index signal in the VJoin signal drop
  down. As a first step this strategy tries to find a good place to put the
  first part. This is done by finding all the places where the mean value of
  the first parts is passed in the reference signal. All these places are tried
  in order and the best match (in a least squares sense) is chosen as the
  starting point for the first part. All other parts are then moved the same
  distance so that they keep their offsets between each other. As a last step
  all parts are individually optimized using the same least square optimization
  as in the *OptimizationLSF* strategy.
"""
import numpy as np

from sympathy.api import qt as qt_compat
QtGui = qt_compat.import_module('QtGui') # noqa

from sympathy.api import node as synode
from sympathy.api import node_helper
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sympathy.api.exceptions import SyDataError, sywarn
from sylib.time_synchronize_gui import TimeSynchronizeWidget
from sylib.synchronize import SynchronizeTime


def _verify_parameters(params):
    try:
        valid = all([params['refsystem'].value,
                     params['refsignal'].value,
                     params['synceesystem'].value,
                     params['synceesignal'].value,
                     params['syncstrategy'].value])
        valid &= ('threshold' in params)
    except:
        valid = False
    return valid


def _write_sync_offset(params, in_datafile, out_datafile):
    refsystem = params['refsystem'].value
    refsignal = params['refsignal'].value

    synceesystem = params['synceesystem'].value
    synceesignal = params['synceesignal'].value

    threshold = float(params['threshold'].value)
    syncstrategy = params['syncstrategy'].value
    vjoin_name = params['vjoin_index'].value or None

    sync = SynchronizeTime()
    sync_offsets = sync.synchronize_file(
        in_datafile, refsignal, synceesignal, threshold,
        syncstrategy, vjoin_name)
    meta_rows = out_datafile.meta.to_table().number_of_rows() or 1

    if sync_offsets is None:
        sync_offsets = [None] * meta_rows
    if len(sync_offsets) == 1:
        sync_offsets = sync_offsets * meta_rows
    if len(sync_offsets) != meta_rows:
        raise SyDataError('Inconsistent number of parts. Try choosing '
                          'another VJoin index column.')
    if any([offset is None for offset in sync_offsets]):
        sywarn(u"Some files could not be synchronized. See meta column "
               u"'SYNC_PERFORMED_{}_{}' in output for details.".format(
                   refsystem.upper(), synceesystem.upper()))

    sync.write_to_file(
        in_datafile, out_datafile, sync_offsets, synceesystem, vjoin_name)

    sync_performed_name = 'SYNC_PERFORMED_{}_{}'.format(
        refsystem.upper(), synceesystem.upper())
    sync_offset_name = 'SYNC_OFFSET_{}_{}'.format(
        refsystem.upper(), synceesystem.upper())

    sync_performed = np.array([
        offset is not None for offset in sync_offsets])
    sync_offsets = np.array([
        offset if offset is not None else 0 for offset in sync_offsets])

    out_datafile.meta.create_column(
        sync_performed_name, sync_performed, {})
    out_datafile.meta.create_column(
        sync_offset_name, sync_offsets, {'unit': 's'})


def _get_base_parameters():
    parameters = synode.parameters()
    parameters.set_string(
        "refsystem", label='Reference system',
        description="Selected reference system", value="")
    parameters.set_string(
        "refsignal", label='Reference signal',
        description="Selected reference signal", value="")
    parameters.set_string(
        "synceesystem", label='Syncee system',
        description="Selected syncee system", value="")
    parameters.set_string(
        "synceesignal", label='Syncee signal',
        description="Selected syncee signal", value="")
    parameters.set_float(
        "threshold", label='Threshold',
        description="Set threshold", value=10.0)
    parameters.set_string(
        "syncstrategy", label='Synchronization strategy',
        description="Selected synchronization strategy",
        value="Sync parts")
    parameters.set_string(
        "vjoin_index", label='Index',
        description="Signal used to find different parts",
        value="")
    return parameters


class TimeSyncADAF(synode.Node):
    """
    Sympathy node for time synchronization of timebases located in different
    systems in the incoming ADAF. An offset is calculated and used to shift
    the timebases in one of the considered systems in the outgoing ADAF.

    :Ref. nodes: :ref:`TimeSync ADAFs`
    """

    name = "TimeSync ADAF"
    description = "Synchronize time between systems."
    icon = "time_sync.svg"
    nodeid = "org.sysess.sympathy.data.adaf.timesyncadaf"
    author = "Alexander Busck <alexander.busck@combine.se>"
    copyright = "(c) 2013 Combine Control Systems AB"
    version = '1.0'
    tags = Tags(Tag.Analysis.SignalProcessing)
    inputs = Ports([Port.ADAF('Input ADAF', name='port1', requiresdata=True)])
    outputs = Ports([Port.ADAF('Synchronized ADAF', name='port1')])

    parameters = _get_base_parameters()

    def verify_parameters(self, node_context):
        return _verify_parameters(node_context.parameters)

    def update_parameters(self, params):
        if 'synceeoffset' in params:
            del params['synceeoffset']

    def exec_parameter_view(self, node_context):
        return TimeSynchronizeWidget(node_context.parameters,
                                     node_context.input['port1'])

    def execute(self, node_context):
        in_datafile = node_context.input['port1']
        out_datafile = node_context.output['port1']
        out_datafile.source(in_datafile)
        _write_sync_offset(node_context.parameters, in_datafile, out_datafile)


TimeSyncADAFs = node_helper.list_node_factory(
    TimeSyncADAF, ['port1'], ['port1'],
    nodeid="org.sysess.sympathy.data.adaf.timesyncadafmultiple")
