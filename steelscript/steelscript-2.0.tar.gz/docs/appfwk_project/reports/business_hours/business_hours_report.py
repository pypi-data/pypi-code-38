# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import steelscript.appfwk.apps.report.modules.c3 as c3
import steelscript.appfwk.apps.report.modules.tables as tables
import steelscript.appfwk.business_hours.datasource.business_hours_source as \
    bizhours
import steelscript.netprofiler.appfwk.libs.profiler_tools as protools
from steelscript.appfwk.apps.report.models import Report
from steelscript.netprofiler.appfwk.datasources import netprofiler
from steelscript.netprofiler.appfwk.datasources import netprofiler_devices

report = Report.create("Business Hour Reporting - NetProfiler Interfaces",
                       position=10,
                       field_order=['starttime',
                                    'endtime',
                                    'netprofiler_filterexpr',
                                    'business_hours_start',
                                    'business_hours_end',
                                    'business_hours_tzname',
                                    'business_hours_weekends'],
                       hidden_fields=['duration', 'resolution'])

report.add_section()

#
# Define by-interface table from NetProfiler
#
basetable = netprofiler.NetProfilerGroupbyTable.create('bh-basetable',
                                                       groupby='interface',
                                                       duration=60,
                                                       resolution=3600,
                                                       interface=True)

# Define all of your columns here associated with basetable
# For each data column (iskey=False), you must specify the aggregation method
# in the bizhours.create below.
basetable.add_column('interface_dns', 'Interface', iskey=True,
                     datatype="string")
basetable.add_column('interface_alias', 'Ifalias', iskey=True,
                     datatype="string")
basetable.add_column('avg_util', '% Utilization', units='pct',
                     sortdesc=True)
basetable.add_column('in_avg_util', '% Utilization In', units='pct')
basetable.add_column('out_avg_util', '% Utilization Out', units='pct')

# The 'aggregate' parameter describes how similar rows on different business
# days should be combined.  For example:
#
#     Day    Total Bytes   Avg Bytes/s
# ---------  ------------  -----------
#     Mon    28MB            100
#     Tue    56MB            200
# ========== ============= ===========
# Combined   84MB            150
# Method     sum             avg
#
# Common methods:
#   sum    - just add up all the data, typical for totals
#   avg    - compute average (using time as a weight), for anything "average"
#   min    - minimum of all values
#   max    - maximum of all values
#
biztable = bizhours.BusinessHoursTable.create('bh-biztable', basetable,
                                              aggregate={
                                                  'avg_util': 'avg',
                                                  'in_avg_util': 'avg',
                                                  'out_avg_util': 'avg'
                                              })

# Device Table

devtable = netprofiler_devices.NetProfilerDeviceTable.create('devtable')
devtable.add_column('ipaddr', 'Device IP', iskey=True,
                    datatype="string")
devtable.add_column('name', 'Device Name', datatype="string")
devtable.add_column('type', 'Flow Type', datatype="string")
devtable.add_column('version', 'Flow Version', datatype="string")

interfaces = protools.ProfilerMergeIpDeviceTable.create('bh-interfaces',
                                                        devtable, biztable)

report.add_widget(tables.TableWidget, interfaces, "Interface", height=600)
report.add_widget(c3.BarWidget, interfaces, "Interface Utilization",
                  height=600, keycols=['interface_name'],
                  valuecols=['avg_util'])

report.add_widget(tables.TableWidget, bizhours.get_timestable(biztable),
                  "Covered times", width=12, height=200)
