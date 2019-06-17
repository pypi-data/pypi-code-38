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
<p> This report demonstrates computing a trend line using
ordinary least squares and extraploating that trend into the future.

<ul>
<li> Custom <a href='/admin/steelscript.qos/qosinterface/'> QoS Interface</a>
     database table editable via the <a href='/admin'>Admin Panel</a>.
<li> Interface is a drop down list based on the QoS Interface entries
<li> Hardcoded widget for EF
<li> Timeseries chart for the requested timeframe
<li> Timeseries chart with trend and extrapolation into the future
     by a multiple of the requested timeframe
</ul>
<ul>
"""

#
# Create the report
#
report = Report.create(
    'VoIP I', position=12.1, description=description,
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
# Section per DSCP
#  - netprofiler_filterexpr
#        = "set any [{direction} interface {interface}]
#           with set any [dscp {dscp}]"
#    - direction is hardcoded from the inner loop
#    - interface comes from the field
#    - dscp is hardcoded from the outer loop
#
section = report.add_section(
    'inbound EF',
    section_keywords=['netprofiler_filterexpr'])

section.fields.add(netprofiler_filterexpr)

NetProfilerTable.extend_filterexpr(
    section, keyword='interface_filterexpr',
    template=('set any [inbound interface {interface}] '
              'with set any [dscp EF]'))

#
# The source data table, grabs the data at 1 minute resolution
#
p = NetProfilerTimeSeriesTable.create(
    'voip1-base', interface=True)

p.add_column('time', 'Time', datatype='time', iskey=True)
p.add_column('avg_bytes', 'Avg Bytes/s', units='B/s')
p.add_column('avg_bits', 'Avg Bits/s', units='b/s',
             synthetic=True, compute_expression='8*{avg_bytes}')

#
# Resample to the requested resolution
#
rs = qs.Resample.create('voip1-base-resampled', p,
                        resample={'avg_bits': 'mean'})
report.add_widget(
    yui3.TimeSeriesWidget, rs,
    'EF - Avg Bits/s Inbound',
    width=6, cols=['avg_bits'])


#
# The time series trend widget
#
trendp = qs.TimeSeriesTrend.create('voip1-trend', rs,
                                   cols=['avg_bits'])
report.add_widget(
    yui3.TimeSeriesWidget, trendp,
    'EF - Avg Bits/s Inbound Trend',
    width=6, cols=['avg_bits', 'avg_bits-trend'])
