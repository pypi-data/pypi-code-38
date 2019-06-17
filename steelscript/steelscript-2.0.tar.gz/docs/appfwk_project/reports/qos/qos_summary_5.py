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
        NetProfilerTimeSeriesTable, NetProfilerGroupbyTable

#
# Description
#
description = """
<p> This report shows how to create a stacked timeseries chart from
individual data source queries.

<ul>
<li> Custom <a href='/admin/steelscript.qos/qosinterface/'> QoS Interface</a>
     database table editable via the <a href='/admin'>Admin Panel</a>.
<li> Interface is a drop down list based on the QoS Interface entries
<li> Hardcoded widgets for EF, AF42 and Default QoS classes.
<li> Metrics are in bits.
<li> Stacked timeseries chart that is computed from for underlying queries:
     EF, AF42, Default, and Total.  Other is computed on the fly.
</ul>
"""

#
# Create the report
#
report = Report.create(
    'QoS Summary V', position=11.5, description=description,
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
base = NetProfilerTimeSeriesTable.create('qs5-overall-in-base', interface=True)

base.add_column('time', 'Time', datatype='time', iskey=True)
base.add_column('in_avg_bytes', 'Avg Bytes/s Inbound', units='B/s')
base.add_column('in_avg_bits', 'Avg Bits/s Inbound', units='b/s',
                synthetic=True, compute_expression=('8*{in_avg_bytes}'))

# Define a Overall TimeSeries showing In/Out Bytes/s
p = qs.qs5_StackedTimeSeriesTable.create(
    'qs5-overall-in', base, col='in_avg_bits', qos=['EF', 'AF42', 'Default'])

report.add_widget(yui3.TimeSeriesWidget, p,
                  'Avg Bits/s Inbound', width=6, stacked=True)

#
# QOS Summary Tables
#

#
# Section per QoS
#  - netprofiler_filterexpr = '{direction} interface {interface}'
#    - direction is hardcoded from the loop
#    - interface comes from the field
#
section = report.add_section('in', section_keywords=['netprofiler_filterexpr'])

section.fields.add(netprofiler_filterexpr)

NetProfilerTable.extend_filterexpr(
    section, keyword='interface_filterexpr',
    template=('inbound interface {interface}'))

p = NetProfilerGroupbyTable.create('qs5-inbountd',
                                   groupby='dsc',
                                   interface=True)

p.add_column('dscp_name', 'Dscp Name', iskey=True, datatype='string')
p.add_column('dscp', 'Dscp', iskey=True, datatype='integer')
p.add_column('avg_bytes', 'Avg Bytes/s', units='B/s')
p.add_column('avg_bits', 'Avg Bits/s', units='b/s', sortdesc=True,
             synthetic=True, compute_expression='8*{avg_bytes}')
p.add_column('peak_bytes', 'Peak Bytes/s', units='B/s')
p.add_column('peak_bits', 'Peak Bits/s', units='b/s', sortdesc=True,
             synthetic=True, compute_expression='8*{peak_bytes}')
p.add_column('total_bytes', 'Total Bytes', units='B')
p.add_column('total_bits', 'Total Bits', units='b',
             synthetic=True, compute_expression='8*{total_bytes}')
p.add_column('avg_util', 'Avg Util', units='pct')
p.add_column('peak_util', 'Peak Util', units='pct')

report.add_widget(yui3.TableWidget, p,
                  'Inbound Traffic by DSCP', width=6,
                  cols=['dscp_name', 'dscp', 'avg_util',
                        'peak_util', 'avg_bits', 'peak_bits',
                        'total_bits'])

#
# Dscp sections: EF, AF41, and Default
#
for dscp in ['EF', 'AF41', 'Default']:

    report.add_section('DSCP %s' % dscp)

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
        'inbound %s' % (dscp),
        section_keywords=['netprofiler_filterexpr'])

    section.fields.add(netprofiler_filterexpr)

    NetProfilerTable.extend_filterexpr(
        section, keyword='interface_filterexpr',
        template=(('set any [inbound interface {interface}] '
                   'with set any [dscp %s]') % (dscp)))

    p = NetProfilerTimeSeriesTable.create(
        'qs5-%s-inbound' % (dscp), interface=True)

    p.add_column('time', 'Time', datatype='time', iskey=True)
    p.add_column('avg_bytes', 'Avg Bytes/s', units='B/s')
    p.add_column('avg_bits', 'Avg Bits/s', units='B/s',
                 synthetic=True, compute_expression='8*{avg_bytes}')

    report.add_widget(
        yui3.TimeSeriesWidget, p,
        '%s - Avg Bits/s Inbound' % (dscp),
        width=4, cols=['avg_bits'])
