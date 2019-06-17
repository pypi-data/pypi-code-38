# Copyright (c) 2017 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from steelscript.appfwk.apps.report.models import Report
import steelscript.appfwk.apps.report.modules.tables as tables

from steelscript.steelhead.appfwk.datasources.steelhead import \
    BatchSteelHeadTable


description = """
<div style="width:500px">
<p>This example report runs a command against a group of steelheads with
same tag. Command examples include:

<p style="margin-left: 40px"><strong>show version</strong>
<p style="margin-left: 40px"><strong>show interfaces</strong>
<p style="margin-left: 40px"><strong>show flows</strong>
<p style="margin-left: 40px"><strong>show stats bandwidth all
bi-directional 5min</strong>

</div>
"""

report = Report.create("SteelHead Batch Report", description=description)

report.add_section()

t = BatchSteelHeadTable.create('batch-steelhead', cacheable=False)

report.add_widget(tables.TableWidget, t, 'batch-sh',
                  width=12, height=0, searching=True)
