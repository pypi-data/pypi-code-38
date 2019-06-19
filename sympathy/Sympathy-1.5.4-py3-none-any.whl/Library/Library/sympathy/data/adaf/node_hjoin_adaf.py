# -*- coding: utf-8 -*-
# Copyright (c) 2013, 2016, 2017, Combine Control Systems AB
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
The horisontal join, or the HJoin, of :ref:`ADAF` objects has the purpose
to merge data that has been simultaneously collected by different measurement
systems and been imported into different ADAFs. The output of the
operation is a new ADAF, where each data container is the result of a
horisontal join between the two corresponding data containers of the
incoming ADAFs.

The content of the metadata and the result containers are tables and
the horisontal join of these containers follows the procedure described
in :ref:`HJoin Table`.

The timeseries container has the structure of a dictionary, where the keys
at the first instance/level are the names of the systems from which the
time resolved data is collected from. The result of a horisontal join
operation upon two timeseries containers will become a new
container to which the content of the initial containers have been added.
In this process it is important to remember that a system in the outgoing
container will be overwritten if one adds a new system with the same name.

In other terms, HJoining an ADAF with another will horisontally join the Meta
and Result sections in the same way as :ref:`HJoin Table`, and add the systems
to the list of system. The systems themselves will not be horisontally joined.
The column names in Meta and Res must have different names, or else the latest
instance will overwrite the previous. The same holds true for the systems.
"""
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
from sympathy.api import node as synode, adaf
from sympathy.api import node_helper
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags


def parameter_base():
    parameters = synode.parameters()
    parameters.set_boolean(
        'merge',
        label='Merge rasters',
        description='If rasters have the same name, merge them',
        value=False)
    return parameters


def hjoin_rasters(adaf1, adaf2):
    """
    Horizontally join any rasters with the same name in another ADAF,
    which contains one or many systems with the same name in both ADAFs.
    """
    for system in adaf2.sys.keys():
        if system in adaf1.sys:
            system1 = adaf1.sys[system]
            system2 = adaf2.sys[system]
            for raster in system2.keys():
                bname = adaf.RasterN.BASIS_NAME
                if raster in system1:
                    base1 = system1[raster].basis_column().value()
                    base2 = system2[raster].basis_column().value()

                    if (base1.dtype == base2.dtype and len(base1) == len(base2)
                            and (base1 == base2).all()):
                        table1 = system1[raster].to_table(basis_name=bname)
                        table1.hjoin(system2[raster].to_table())
                        system1[raster].from_table(table1, basis_name=bname)
                    else:
                        print(
                            'Rasters are of differing type and/or length. The '
                            'merge for raster "{}" in system "{}" has not '
                            'been performed, just the regular ADAF HJoin.'
                            .format(raster, system))
                else:
                    adaf1.sys[system].copy(raster, adaf2.sys[system])
        else:
            adaf1.sys.copy(system, adaf2.sys)


def hjoin(adaf1, adaf2, merge):
    adaf1.meta.hjoin(adaf2.meta)
    adaf1.res.hjoin(adaf2.res)
    if merge:
        hjoin_rasters(adaf1, adaf2)
    else:
        adaf1.sys.hjoin(adaf2.sys)


class HJoinSuper(synode.Node):
    copyright = '(c) 2016-2017 Combine Control Systems AB'
    icon = 'hjoin_adaf.svg'
    tags = Tags(Tag.DataProcessing.TransformStructure)


class HJoinADAF(HJoinSuper):
    """Horistonal join, or HJoin, of two ADAFs into an ADAF."""

    name = "HJoin ADAF"
    description = "HJoin two ADAF files."
    nodeid = "org.sysess.sympathy.data.adaf.hjoinadaf"
    author = "Alexander Busck <alexander.busck@combine.se>"
    version = '1.1'

    inputs = Ports([
        Port.ADAF('ADAF 1', name='port1'),
        Port.ADAF('ADAF 2', name='port2')])
    outputs = Ports([Port.ADAF('Joined ADAF', name='port1')])

    parameters = parameter_base()

    def execute(self, node_context):
        adaffile1 = node_context.input['port1']
        adaffile2 = node_context.input['port2']
        out_adaffile = node_context.output['port1']
        merge = node_context.parameters['merge'].value
        out_adaffile.source(adaffile1)
        hjoin(out_adaffile, adaffile2, merge)


HJoinADAFs = node_helper.list_node_factory(
    HJoinADAF,
    ['port1', 'port2'], ['port1'],
    name="HJoin ADAFs pairwise",
    nodeid="org.sysess.sympathy.data.adaf.hjoinadafs")


class HJoinADAFsList(HJoinSuper):
    """
    Horizontal join of a list of ADAFs into one ADAF. This means that
    all systems in each ADAF is are congregated into one ADAF with many
    systems.
    Using the option 'Use index as prefix' will result in columns and systems
    results in systems' names getting the list index of the ADAF as a prefix
    to keep systems with the same names.
    Meta data and results will be joined horizontally with the same prefixing.
    Unchecking the option results in the same behaviour as Hjoin ADAFs
    where all but the latest instance are discarded.
    """

    name = "HJoin ADAFs"
    description = 'Combine ADAFs into one ADAF with many systems'
    nodeid = 'org.sysess.sympathy.data.adaf.hjoinadafslist'
    author = 'Andreas Tågerud<andreas.tagerud@combine.se>'
    version = '1.1'

    inputs = Ports([Port.ADAFs('ADAFs list', name='port1')])
    outputs = Ports([Port.ADAF('Joined ADAFs', name='port1')])

    parameters = parameter_base()

    def execute(self, node_context):
        input_list = node_context.input['port1']
        output = node_context.output['port1']
        merge = node_context.parameters['merge'].value
        input_iter = iter(input_list)

        try:
            first = next(input_iter)
        except StopIteration:
            pass
        else:
            output.source(first)

            for input_ in input_iter:
                hjoin(output, input_, merge)

    def update_parameters(self, parameters):
        if 'rename' in parameters:
            del parameters['rename']
