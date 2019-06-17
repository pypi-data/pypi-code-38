# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

"""
LPSS Report
"""

from steelscript.appfwk.apps.report.models import Report
import steelscript.appfwk.apps.report.modules.tables as tables
import steelscript.lpss.appfwk.datasources.lpss_collection as lpss_collect

report = Report.create("LPSS Merge Report (Test Data)", position=14)
report.add_section()


#
# Merge
#
basetable = lpss_collect.LPSSTestDataTable.create(name='lpss_collect_testdata')

merge = lpss_collect.MergeTable.create(name='lpss_merge', basetable=basetable)

report.add_widget(tables.TableWidget, merge, 'Merged LPSS Data',
                  height=500, width=12)
