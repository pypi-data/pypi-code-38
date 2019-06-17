# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

"""
LPSS Report
"""
from steelscript.appfwk.apps.datasource.modules.analysis import AnalysisTable
from steelscript.appfwk.apps.report.models import Report
import steelscript.appfwk.apps.report.modules.c3 as c3
import steelscript.appfwk.apps.report.modules.tables as tables
import steelscript.lpss.appfwk.datasources.lpss_collection as lpss_collect

report = Report.create("LPSS Merge Plot Report (Test Data)", position=14)
report.add_section()


#
# Merge
#
basetable = lpss_collect.LPSSTestDataTable.create(name='lpss_collect_merge_testdata')

merge = lpss_collect.MergeTable.create(name='lpss_merge', basetable=basetable)

report.add_widget(tables.TableWidget, merge, 'Merged LPSS Data', width=12)

# APP VS PKT
plot = AnalysisTable.create('appvspkt',
                            tables={'src': merge},
                            function=lpss_collect.app_vs_pkt)
plot.add_column('timestamp', label='LPSS Timestamp', iskey=True,
                datatype='time')
plot.add_column('app_vs_pkt_a', label='app_vs_pkt_a', datatype='float')
plot.add_column('app_vs_pkt_b', label='app_vs_pkt_b', datatype='float')

report.add_widget(c3.TimeSeriesWidget, plot,
                  'App vs Pkt A and App vs Pkt B over time.', width=12)


# APP A VS DELAY
plot = AnalysisTable.create('appavsdelay',
                            tables={'src': merge},
                            function=lpss_collect.appa_vs_delay)
plot.add_column('timestamp', label='LPSS Timestamp', iskey=True,
                datatype='time')
plot.add_column('app_vs_pkt_a', label='app_vs_pkt_a', datatype='float')
plot.add_column('delay', label='delay', datatype='float')

report.add_widget(c3.TimeSeriesWidget, plot,
                  'App B vs Delay.', width=6)


# APP B VS DELAY
plot = AnalysisTable.create('appbvsdelay',
                            tables={'src': merge},
                            function=lpss_collect.appb_vs_delay)
plot.add_column('timestamp', label='LPSS Timestamp', iskey=True,
                datatype='time')
plot.add_column('app_vs_pkt_b', label='app_vs_pkt_b', datatype='float')
plot.add_column('delay', label='delay', datatype='float')

report.add_widget(c3.TimeSeriesWidget, plot,
                  'App B vs Delay.', width=6)
