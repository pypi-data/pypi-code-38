# Copyright (c) 2017 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


from steelscript.appfwk.apps.report.models import Report
import steelscript.appfwk.apps.report.modules.tables as tables

from steelscript.steelhead.appfwk.datasources.steelhead import \
    ProductInfoTable, InterfacesTable, FlowsTable, BandwidthTable


report = Report.create("Single SteelHead Report", position=10)

report.add_section()

t = ProductInfoTable.create('product-info', cacheable=False)
t.add_column('model', 'Model', datatype='string')
t.add_column('name', 'Name', datatype='string')
t.add_column('release', 'Release', datatype='string')

report.add_widget(tables.TableWidget, t, "Product Info", width=12, height=150)

t = InterfacesTable.create('interfaces-running', cacheable=False)
t.add_column('name', 'Name', datatype='string')
t.add_column('link', 'Link', datatype='string')
t.add_column('up', 'Up', datatype='string')
t.add_column('speed', 'Speed', datatype='string')
t.add_column('duplex', 'Duplex', datatype='string')
t.add_column('mtu', 'MTU', datatype='string')
t.add_column('hw address', 'HW Address', datatype='string')
t.add_column('interface type', 'Interface Type', datatype='string')
t.add_column('ip address', 'IP Address', datatype='string')
t.add_column('netmask', 'NetMask', datatype='string')
t.add_column('ipv6 link-local address', 'IPV6 Address', datatype='string')
t.add_column('traffic status', 'Traffic Status', datatype='string')
t.add_column('counters cleared date', 'Counters Cleared', datatype='string')

report.add_widget(tables.TableWidget, t, "State of Interfaces",
                  width=12, height=0, searching=True)

t = FlowsTable.create('flows', cacheable=False)
t.add_column('category', 'Category', datatype='string')
t.add_column('all', 'All', datatype='integer')
t.add_column('v4', 'V4', datatype='integer')
t.add_column('v6', 'V6', datatype='integer')
report.add_widget(tables.TableWidget, t, "Flows", width=12, height=0)

t = BandwidthTable.create('bandwidth', cacheable=False)
t.add_column('direction', 'Direction', datatype='string')
t.add_column('capacity increase', 'Capacity Increase', datatype='string')
t.add_column('lan data', 'Lan Data', datatype='string')
t.add_column('wan data', 'Wan Data', datatype='string')
t.add_column('data reduction', 'Data Reduction', datatype='string')
t.add_column('data reduction peak', 'Data Reduction Peak', datatype='string')
t.add_column('data reduction peak time', 'Data Reduction Peak Time',
             datatype='string')
report.add_widget(tables.TableWidget, t, "Bandwidth",
                  width=12, height=200)
