# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import steelscript.appfwk.apps.report.modules.c3 as c3
from steelscript.appfwk.apps.report.models import Report
import steelscript.appfwk.apps.report.modules.tables as tables

import steelscript.appfwk.business_hours.datasource.business_hours_source as \
    bizhours
from steelscript.netprofiler.appfwk.datasources import netprofiler

report = Report.create("Business Hour Reporting - By Application",
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
basetable = netprofiler.NetProfilerGroupbyTable.create('bh-basetable-byapp',
                                                       groupby='application',
                                                       duration=60,
                                                       resolution=3600,
                                                       interface=True)

# Define all of your columns here associated with basetable
# For each data column (iskey=False), you must specify the aggregation method
# in the bizhours.create below.
basetable.add_column('app_name', 'Application', iskey=True,
                     datatype="string")
basetable.add_column('network_rtt', 'Network RTT', datatype='integer',
                     units='ms', sortdesc=True)
basetable.add_column('in_avg_bytes', 'Avg Bytes In', units='B')
basetable.add_column('out_avg_bytes', 'Avg Bytes Out', units='B')

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
biztable = bizhours.BusinessHoursTable.create('bh-biztable-byapp', basetable,
                                              aggregate={
                                                  'network_rtt': 'max',
                                                  'in_avg_bytes': 'avg',
                                                  'out_avg_bytes': 'avg'
                                              })

report.add_widget(tables.TableWidget, biztable, "Applications", height=600)
report.add_widget(c3.BarWidget, biztable, "Applications RTT", height=600,
                  keycols=['app_name'], valuecols=['network_rtt'])

report.add_widget(tables.TableWidget, bizhours.get_timestable(biztable),
                  "Covered times", width=12, height=200)
