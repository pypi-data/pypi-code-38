# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License').  This software is distributed "AS IS"
# as set forth in the License.

from steelscript.appfwk.apps.datasource.models import TableField
from steelscript.appfwk.apps.report.models import Report
import steelscript.appfwk.apps.report.modules.yui3 as yui3

import steelscript.appfwk.business_hours.datasource.business_hours_source \
    as bizhours

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
<p> This report builds on computing a 95th percentile over business hours
only, computing the value for each day and generating a new timeseries.

<ul>
<li> Custom <a href='/admin/steelscript.qos/qosinterface/'> QoS Interface</a>
     database table editable via the <a href='/admin'>Admin Panel</a>.
<li> Interface is a drop down list based on the QoS Interface entries
<li> Hardcoded widget for EF
<li> Filter on business hours
<li> Compute 95th percentile for each day, and graph as timeseries
</ul>
"""

#
# Create the report
#
report = Report.create(
    'VoIP V', position=12.5, description=description,
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
base = NetProfilerTimeSeriesTable.create(
    'voip5-base', interface=True)

base.add_column('time', 'Time', datatype='time', iskey=True)
base.add_column('avg_bytes', 'Avg Bytes/s', units='B/s')
base.add_column('avg_bits', 'Avg Bits/s', units='b/s',
                synthetic=True, compute_expression='8*{avg_bytes}')

biztable = bizhours.BusinessHoursTable.create('voip5-biztable', base,
                                              aggregate={'avg_bits': 'mean'})

p = qs.voip4_95PerDayTimeSeriesTable.create('voip5-95perday', biztable,
                                            cols=['avg_bits'])


#
# The time series trend widget
#
trendp = qs.TimeSeriesTrend.create('voip5-trend', p,
                                   cols=['avg_bits'])


result = qs.AddQosInterfaceFieldTable.create(
    'voip5-result', trendp, field='EF_limit', field_label='EF limit')

report.add_widget(
    yui3.TimeSeriesWidget, result,
    'EF - Avg Bits/s Inbound - 95 percential per day trend',
    width=12, cols=['avg_bits', 'avg_bits-trend', 'EF_limit'])
