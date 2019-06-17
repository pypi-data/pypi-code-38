# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from steelscript.appfwk.apps.report.models import Report
import steelscript.appfwk.apps.report.modules.raw as raw

# Import the datasource module for this plugin (if needed)
from steelscript.hero.appfwk.datasources.hero_source import \
    HeroPcapUploadTable


report = Report(title="PCAP Upload", position=11)
report.save()

report.add_section()

#
# Table: Process Pcap files
#
table = HeroPcapUploadTable.create('pcap')

report.add_widget(raw.TableWidget, table, 'PCAP Upload', width=12, height=200)