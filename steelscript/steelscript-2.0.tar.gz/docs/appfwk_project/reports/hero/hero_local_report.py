# Copyright (c) 2016 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


import steelscript.appfwk.apps.datasource.modules.analysis as analysis
from steelscript.appfwk.apps.report.models import Report
from steelscript.appfwk.apps.datasource.models import Column, TableField
import steelscript.appfwk.apps.report.modules.tables as tables

# Import the datasource module for this plugin (if needed)
from steelscript.hero.appfwk.datasources.hero_source import \
    HeroLocalTable


report = Report.create(title="CIFS Performance From PCAP Data",
                       field_order=['pcapfilename',
                                    'assumed_rtt',
                                    'local_rtt',
                                    'assumed_fte_cost',
                                    'summary_rows'],
                       position=11)
report.add_section()

table = HeroLocalTable.create('CIFS_PCAP_Performance')

table.add_column('cifs_file_path', 'File Path',
                 datatype=Column.DATATYPE_STRING, iskey=True)
table.add_column('bytes', 'Bytes',
                 datatype=Column.DATATYPE_INTEGER, iskey=True)
table.add_column('command_count', 'SMB Command Count',
                 datatype=Column.DATATYPE_INTEGER)
table.add_column('total_secs_saved', 'Total Seconds Saved')
table.add_column('total_dollars_saved', 'Total Dollars Saved')


report.add_widget(tables.TableWidget,
                  table,
                  'CIFS_Performance by File Path',
                  paging=False,
                  width=12,
                  height=0)