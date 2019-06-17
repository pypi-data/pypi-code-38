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
<p> This report adds in comparison against the interface speed.

<ul>
<li> Custom <a href='/admin/steelscript.qos/qosinterface/'> QoS Interface</a>
     database table editable via the <a href='/admin'>Admin Panel</a>.
<li> Interface is a drop down list based on the QoS Interface entries
<li> Timeseries chart showing inbound/outbound utilization.
<li> Interface speed is read from database, plotted on graph as well as
     in comparison table
</ul>
"""

#
# Create the report
#
report = Report.create(
    'QoS Summary VI', position=11.6, description=description,
    field_order=['restricted_time', 'interface'],
    hidden_fields=['netprofiler_filterexpr',
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
base = NetProfilerTimeSeriesTable.create('qs6-overall-base', interface=True)

base.add_column('time', 'Time', datatype='time', iskey=True)
base.add_column('in_avg_bytes', 'Avg Bytes/s Inbound', units='B/s')
base.add_column('in_avg_bits', 'Avg Bits/s Inbound', units='b/s',
                synthetic=True, compute_expression=('8*{in_avg_bytes}'))

base.add_column('out_avg_bytes', 'Avg Bytes/s Outbound', units='B/s')
base.add_column('out_avg_bits', 'Avg Bits/s Outbound', units='b/s',
                synthetic=True, compute_expression=('8*{out_avg_bytes}'))

# Define a Overall TimeSeries showing In/Out Bytes/s
p = qs.qs6_AddInterfaceSpeedTable.create('qs6-ifspeed', base)

report.add_widget(yui3.TimeSeriesWidget, p,
                  'Avg Bits/s', width=6,
                  cols=['in_avg_bits', 'out_avg_bits', 'ifspeed'])

# Define a Overall TimeSeries showing In/Out Bytes/s
p = qs.qs6_NearInterfaceSpeedTable.create('qs6-ifspeed-range', base,
                                          cols=['in_avg_bits', 'out_avg_bits'])

report.add_widget(yui3.TableWidget, p,
                  'Percentage of samples relative to inteface speed', width=6)
