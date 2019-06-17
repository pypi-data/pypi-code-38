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
<p> This shows the times when video on AF41 is likely congested and dropping
    due to near 100% link utilization.

<ul>
<li> Custom <a href='/admin/steelscript.qos/qosinterface/'> QoS Interface</a>
     database table editable via the <a href='/admin'>Admin Panel</a>.
<li> Interface is a drop down list based on the QoS Interface entries
<li> Hardcoded widget for AF41 - Video
<li> Timeseries chart for AF41 over the limit <i>only</i> during times
     when the interface is nearing 100% utilization.
<li> Table summarizing the relevant information for this interface

</ul>
"""

#
# Create the report
#
report = Report.create(
    'Video III', position=13.3, description=description,
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
    'video3-af41-base', interface=True)

p.add_column('time', 'Time', datatype='time', iskey=True)
p.add_column('avg_bytes', 'Avg Bytes/s', units='B/s')
p.add_column('avg_bits', 'Avg Bits/s', units='b/s',
             synthetic=True, compute_expression='8*{avg_bytes}')

#
# Resample to the requested resolution
#
rs = qs.Resample.create('video3-af41-base-resampled', p,
                        resample={'avg_bits': 'mean'})

#
# Overage
#
overage = qs.video3_OverageTable.create('video3-overage', rs)

report.add_widget(
    yui3.TimeSeriesWidget, overage,
    'AF41 Overage with expected loss - Avg Bits/s Inbound',
    width=12, cols=['avg_bits'])

pctoverage = qs.video3_PctOverageTable.create('video3-pctoverage', overage)

report.add_widget(
    yui3.TableWidget, pctoverage,
    'AF41 % Time Over', width=12, height=100)

#
# AF41 Limit
#
af41_limit = qs.AddQosInterfaceFieldTable.create(
    'video3-af41-limit', rs, field='AF41_limit', field_label='AF41 limit')

report.add_widget(
    yui3.TimeSeriesWidget, af41_limit,
    'Interface - Avg Bits/s Inbound',
    width=12, cols=['avg_bits', 'AF41_limit'])

#
# Section Overall
#  - netprofiler_filterexpr
#        = "set any [{direction} interface {interface}]"
#    - interface comes from the field
#
section = report.add_section(
    'inbound AF41',
    section_keywords=['netprofiler_filterexpr'])

section.fields.add(netprofiler_filterexpr)

NetProfilerTable.extend_filterexpr(
    section, keyword='interface_filterexpr',
    template=('set any [inbound interface {interface}]'))

#
# Resample to the requested resolution
#
rs = qs.Resample.create('video3-overall-base-resampled', p,
                        resample={'avg_bits': 'mean'})

overall_limit = qs.AddQosInterfaceFieldTable.create(
    'video3-overall-limit', rs, field='speed', field_label='If Speed')

report.add_widget(
    yui3.TimeSeriesWidget, overall_limit,
    'Interface - Avg Bits/s Inbound',
    width=12, cols=['avg_bits', 'speed'])
