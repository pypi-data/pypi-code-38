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
<p> This report is identical to
<a href='/report/qos/qos_summary_1/'>QoS Summary I</a> except that metrics
are in bits instead of bytes.

<ul>
<li> Interface is a text entry field
<li> Hardcoded widgets for EF, AF42 and Default QoS classes.
<li> Metrics are in bits using <i>synthetic</i> columns: bytes * 8
</ul>
"""

#
# Create the report
#
report = Report.create(
    'QoS Summary II', position=11.2, description=description,
    field_order=['restricted_time', 'interface'],
    hidden_fields=['netprofiler_filterexpr',
                   'endtime', 'duration', 'resolution'])

qs.restricted_time_field(obj=report)

# Define a toplevel criteria field that will be the filter expression
# This will be the final NetProfiler advanced traffic filter
# expression based on the interface and qos criteria
netprofiler_filterexpr = TableField.create(
    keyword='netprofiler_filterexpr')

# Define an interface field, this is required
interface_field = TableField.create(
    keyword='interface', label='Interface', required=True)

report.fields.add(interface_field)

#
# Overall section
#  - netprofiler_filterexpr = 'interface {interface}'
#
section = report.add_section('Overall',
                             section_keywords=['netprofiler_filterexpr'])

section.fields.add(netprofiler_filterexpr)
section.fields.add(interface_field)

NetProfilerTable.extend_filterexpr(section, keyword='interface_filterexpr',
                                   template='interface {interface}')

#
# Define a Overall TimeSeries showing In/Out Utilization
#
p = NetProfilerTimeSeriesTable.create('qs2-overall-util', interface=True)

p.add_column('time', 'Time', datatype='time', iskey=True)
p.add_column('in_avg_util', 'Avg Inbound Util %', units='B/s')
p.add_column('out_avg_util', 'Avg Outbound Util %', units='B/s')
report.add_widget(yui3.TimeSeriesWidget, p,
                  '{interface} - Overall Utilization', width=12)

#
# Direction Summary Tables
#
for direction in ['in', 'out']:

    # Define a Overall TimeSeries showing In/Out Bytes/s
    p = NetProfilerTimeSeriesTable.create('qs2-overall-%s' % direction,
                                          interface=True)

    p.add_column('time', 'Time', datatype='time', iskey=True)
    p.add_column('%s_avg_bytes' % direction,
                 'Avg Bytes/s %sbound' % direction.capitalize(), units='B/s')
    p.add_column('%s_avg_bits' % direction,
                 'Avg Bits/s %sbound' % direction.capitalize(), units='b/s',
                 synthetic=True,
                 compute_expression=('8*{%s_avg_bytes}' % direction))

    report.add_widget(yui3.TimeSeriesWidget, p,
                      'Avg Bits/s %sbound' % direction.capitalize(),
                      cols=['%s_avg_bits' % direction], width=6)

#
# QOS Summary Tables
#
for direction in ['inbound', 'outbound']:
    #
    # Section per direction
    #  - netprofiler_filterexpr = '{direction} interface {interface}'
    #    - direction is hardcoded from the loop
    #    - interface comes from the field
    #
    section = report.add_section('%s' % direction,
                                 section_keywords=['netprofiler_filterexpr'])

    section.fields.add(netprofiler_filterexpr)

    NetProfilerTable.extend_filterexpr(
        section, keyword='interface_filterexpr',
        template=('%s interface {interface}' % direction))

    p = NetProfilerGroupbyTable.create('qs2-%s' % direction,
                                       groupby='dsc',
                                       interface=True)

    p.add_column('dscp_name', 'Dscp Name', iskey=True, datatype='string')
    p.add_column('dscp', 'Dscp', iskey=True, datatype='integer')
    p.add_column('avg_util', 'Avg Util', units='pct', sortdesc=True)
    p.add_column('peak_util', 'Peak Util', units='pct')
    p.add_column('avg_bytes', 'Avg Bytes/s', units='B/s')
    p.add_column('avg_bits', 'Avg Bits/s', units='b/s',
                 synthetic=True, compute_expression='8*{avg_bytes}')
    p.add_column('peak_bytes', 'Peak Bytes/s', units='B/s')
    p.add_column('peak_bits', 'Peak Bits/s', units='b/s',
                 synthetic=True, compute_expression='8*{peak_bytes}')
    p.add_column('total_bytes', 'Total Bytes', units='B')
    p.add_column('total_bits', 'Total Bits', units='b',
                 synthetic=True, compute_expression='8*{total_bytes}')

    report.add_widget(yui3.TableWidget, p,
                      '%s Traffic by DSCP' % direction.capitalize(), width=6,
                      cols=['dscp_name', 'dscp', 'avg_util',
                            'peak_util', 'avg_bits', 'peak_bits',
                            'total_bits'])

#
# Dscp sections: EF, AF41, and Default
#
for dscp in ['EF', 'AF41', 'Default']:

    report.add_section('DSCP %s' % dscp)

    for direction in ['inbound', 'outbound']:
        #
        # Section per direction
        #  - netprofiler_filterexpr
        #        = "set any [{direction} interface {interface}]
        #           with set any [dscp {dscp}]"
        #    - direction is hardcoded from the inner loop
        #    - interface comes from the field
        #    - dscp is hardcoded from the outer loop
        #
        section = report.add_section(
            '%s %s' % (direction, dscp),
            section_keywords=['netprofiler_filterexpr'])

        section.fields.add(netprofiler_filterexpr)
        section.fields.add(interface_field)

        NetProfilerTable.extend_filterexpr(
            section, keyword='interface_filterexpr',
            template=(('set any [%s interface {interface}] '
                       'with set any [dscp %s]') %
                      (direction, dscp)))

        p = NetProfilerTimeSeriesTable.create(
            'qs2-%s-%s' % (dscp, direction), interface=True)

        p.add_column('time', 'Time', datatype='time', iskey=True)
        p.add_column('avg_bytes', 'Avg Bytes/s', units='B/s')
        p.add_column('avg_bits', 'Avg Bits/s', units='B/s',
                     synthetic=True, compute_expression='8*{avg_bytes}')

        report.add_widget(
            yui3.TimeSeriesWidget, p,
            '%s - Avg Bits/s %s' % (dscp, direction.capitalize()),
            width=6, cols=['avg_bits'])
