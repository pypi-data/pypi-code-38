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
<p> This report iterates over all defined interfaces to quickly
    identify potential problem interfaces reaching capacity.

<ul>
<li> Custom <a href='/admin/steelscript.qos/qosinterface/'> QoS Interface</a>
     database table editable via the <a href='/admin'>Admin Panel</a>.
<li> Table and bar chart listing all interfaces defined
<li> Computes histogram style ranges based on
     <a href='/report/qos/qos_summary_6/'>QoS Summary VI</a> for
     each interface.
</ul>
"""

#
# Create the report
#
report = Report.create(
    'QoS Summary VII', position=11.7, description=description,
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
# Overall section
#  - netprofiler_filterexpr = 'interface {interface}'
#
section = report.add_section('Overall',
                             section_keywords=['netprofiler_filterexpr'])

section.fields.add(netprofiler_filterexpr)

NetProfilerTable.extend_filterexpr(section, keyword='interface_filterexpr',
                                   template='interface {interface}')

#
# Inbound Summary Tables
#

NetProfilerTable.extend_filterexpr(
    section, keyword='interface_filterexpr',
    template=('inbound interface {interface}'))

# Define a Overall TimeSeries showing In/Out Bytes/s
ifbase = NetProfilerTimeSeriesTable.create('qs6-overall-ifbase',
                                           interface=True)

ifbase.add_column('time', 'Time', datatype='time', iskey=True)
ifbase.add_column('avg_bytes', 'Avg Bytes/s', units='B/s')
ifbase.add_column('avg_bits', 'Avg Bits/s', units='b/s',
                  synthetic=True, compute_expression=('8*{avg_bytes}'))

# Define a Overall TimeSeries showing In/Out Bytes/s
rangebase = qs.qs6_NearInterfaceSpeedTable.create(
    'qs6-ifspeed-range', ifbase, cols=['avg_bits'],
    limits=[(0, 0.1), (0.1, 0.5), (0.5, 0.95), (0.95, -1)]
    )

rangetable = qs.qs7_RangeTable.create(
    'qs7-ranges', rangebase)

report.add_widget(yui3.TableWidget, rangetable,
                  'Percentage of samples relative to interface speed', width=6)

report.add_widget(yui3.BarWidget, rangetable,
                  'Histogram of busiest 3 interfaces', width=6, rows=3)
