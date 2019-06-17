# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License').  This software is distributed "AS IS"
# as set forth in the License.

from steelscript.appfwk.apps.datasource.models import TableField
from steelscript.appfwk.apps.report.models import Report
import steelscript.appfwk.apps.report.modules.yui3 as yui3

from steelscript.netprofiler.appfwk.datasources.netprofiler import \
    NetProfilerTable

import steelscript.qos.appfwk.datasources.qos_source as qs

sim = True
if sim:
    import steelscript.qos.appfwk.datasources.qos_simdata as qos_simdata
    NetProfilerTimeSeriesTable = qos_simdata.InterfaceTimeSeriesTable
    NetProfilerGroupbyTable = qos_simdata.InterfaceGroupbyTable
else:
    from steelscript.netprofiler.appfwk.datasources.netprofiler import \
        NetProfilerTimeSeriesTable

#
# Description
#
description = """
<p> This report compiles statics for video on AF41 across all interfaces.

<ul>
<li> Custom <a href='/admin/steelscript.qos/qosinterface/'> QoS Interface</a>
     database table editable via the <a href='/admin'>Admin Panel</a>.
<li> Iterate over all interface in the database
<li> Table summarizing interface information with percentage of time
     each interface is over limit <i>only</i> during times when the
     interface is nearing 100% utilization otherwise.
</ul>
"""

#
# Create the report
#
report = Report.create(
    'Video IV', position=13.4, description=description,
    field_order=['restricted_time'],
    hidden_fields=['netprofiler_filterexpr', 'interface',
                   'endtime', 'duration', 'resolution'])

qs.restricted_time_field(obj=report)

# Define a toplevel criteria field that will be the filter expression
# This will be the final NetProfiler advanced traffic filter
# expression based on the interface and qos criteria
netprofiler_filterexpr = TableField.create(
    keyword='netprofiler_filterexpr')

# Define an interface field, this field is based off a custom
# database table defined in steelscript/qos/appfwk/models
interface_field = qs.qos_interface_field(keyword='interface', obj=report)

#
# Section per DSCP
#  - netprofiler_filterexpr
#        = "set any [{direction} interface {interface}]
#           with set any [dscp {dscp}]"
#    - interface comes from the field
#
section = report.add_section(
    'inbound AF41',
    section_keywords=['netprofiler_filterexpr'])

section.fields.add(netprofiler_filterexpr)

NetProfilerTable.extend_filterexpr(
    section, keyword='interface_filterexpr',
    template=('set any [inbound interface {interface}] '
              'with set any [dscp AF41]'))

#
# The source data table, grabs the data at 1 minute resolution
#
p = NetProfilerTimeSeriesTable.create(
    'video4-af41-base', interface=True)

p.add_column('time', 'Time', datatype='time', iskey=True)
p.add_column('avg_bytes', 'Avg Bytes/s', units='B/s')
p.add_column('avg_bits', 'Avg Bits/s', units='b/s',
             synthetic=True, compute_expression='8*{avg_bytes}')

#
# Resample to the requested resolution
#
rs = qs.Resample.create('video4-af41-base-resampled', p,
                        resample={'avg_bits': 'mean'})

#
# Overage
#
overage = qs.video3_OverageTable.create('video4-overage', rs)

pctoverage = qs.video3_PctOverageTable.create('video4-pctoverage', overage)

p = qs.video4_InterfacesOverageTable.create('video4-interfaces-overage',
                                            pctoverage)

report.add_widget(yui3.TableWidget, p,
                  'AF41 usage over all interfaces', width=12)
