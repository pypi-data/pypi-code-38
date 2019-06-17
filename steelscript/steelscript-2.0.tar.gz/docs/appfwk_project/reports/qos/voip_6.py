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
<p> This report computes 95th percential trend for each interface
and compares the result to the configured limit for that interface.

<ul>
<li> Custom <a href='/admin/steelscript.qos/qosinterface/'> QoS Interface</a>
     database table editable via the <a href='/admin'>Admin Panel</a>.
<li> Hardcoded widget for EF
<li> Filter on business hours
<li> Compute 95th percentile for each day
<li> Trend over time, extrapolate into the future
<lI> Report on current and trend values per interface
</ul>
"""

#
# Create the report
#
report = Report.create(
    'VoIP VI', position=12.6, description=description,
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
    'voip6-base', interface=True)

base.add_column('time', 'Time', datatype='time', iskey=True)
base.add_column('avg_bytes', 'Avg Bytes/s', units='B/s')
base.add_column('avg_bits', 'Avg Bits/s', units='b/s',
                synthetic=True, compute_expression='8*{avg_bytes}')

biztable = bizhours.BusinessHoursTable.create('voip6-biztable', base,
                                              aggregate={'avg_bits': 'mean'})

perday = qs.voip4_95PerDayTimeSeriesTable.create('voip6-95perday', biztable,
                                                 cols=['avg_bits'])


#
# The time series trend widget
#
trendbase = qs.TimeSeriesTrend.create('voip6-trendbase', perday,
                                      cols=['avg_bits'])

trend = qs.AddQosInterfaceFieldTable.create(
    'voip6-trend', trendbase, field='EF_limit', field_label='EF limit')

p = qs.voip6_InterfacesTrendTable.create('voip6-interfaces', trend)

report.add_widget(yui3.TableWidget, p,
                  'EF usage across all interfaces', width=12)
