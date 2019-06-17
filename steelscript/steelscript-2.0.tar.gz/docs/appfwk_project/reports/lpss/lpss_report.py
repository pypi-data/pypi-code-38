# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

"""
LPSS Report
"""

from steelscript.appfwk.apps.report.models import Report
from steelscript.appfwk.apps.datasource.models import Column
import steelscript.appfwk.apps.report.modules.c3 as c3
import steelscript.lpss.appfwk.datasources.lpss_reporting_datasource as \
    packet_data

report = Report.create("LPSS Analysis", position=14,
                       field_order=['shark1_pcap_file',
                                    'shark2_pcap_file',
                                    'lpss_port']
                       )

report.add_section()

table = packet_data.LPSSSourceTable.create(name='lpss_src_table')

table.add_column('lpss_timestamp',
                 'LPSS Timestamp',
                 datatype=Column.DATATYPE_TIME,
                 iskey=True)

appvpkt_table = packet_data.AppVsPktTimesTable.create(name='appvpkt',
                                                      tables={'base': table})
appvpkt_table.add_column('lpss_timestamp',
                         'LPSS Timestamp',
                         datatype=Column.DATATYPE_TIME,
                         iskey=True)

appvdelay_table = packet_data.AppPktBvsDelayTimesTable.create(
    name='appvdelay',
    tables={'base': table})
appvdelay_table.add_column('lpss_timestamp',
                           'LPSS Timestamp',
                           datatype=Column.DATATYPE_TIME,
                           iskey=True)

dropped_table = packet_data.DroppedBySecTable.create(
    name='dropped',
    tables={'base': table})
dropped_table.add_column('lpss_timestamp',
                         'LPSS Timestamp',
                         datatype=Column.DATATYPE_TIME,
                         iskey=True)


report.add_widget(c3.TimeSeriesWidget,
                  appvpkt_table,
                  'App vs Pkt A and App vs Pkt B over time.',
                  width=12)

report.add_widget(c3.TimeSeriesWidget,
                  appvdelay_table,
                  'App vs Pkt B against Measured Delay over time.',
                  width=12)

report.add_widget(c3.TimeSeriesWidget,
                  dropped_table,
                  'Dopped LPSS transactions over time.',
                  width=12)
