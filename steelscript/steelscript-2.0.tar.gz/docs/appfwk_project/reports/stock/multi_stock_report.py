# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

"""
This file defines a single report of multiple tables and widgets.

The typical structure is as follows:

    report = Report.create('Stock Report')
    report.add_section()

    table = SomeTable.create(name, table_options...)
    table.add_column(name, column_options...)
    table.add_column(name, column_options...)
    table.add_column(name, column_options...)

    report.add_widget(yui3.TimeSeriesWidget, table, name, width=12)

See the documeantion or sample plugin for more details
"""

from steelscript.appfwk.apps.report.models import Report
import steelscript.appfwk.apps.report.modules.c3 as c3

# Import the datasource module for this plugin (if needed)
import steelscript.stock.appfwk.datasources.stock_source as stock

report = Report.create("Stock Report-Multiple Stocks", position=11)

report.add_section()

#
# Define a stock table with current prices with a list of stocks
#

table = stock.MultiStockPriceTable.create(name='multi-stock-price',
                                          duration='52w', resolution='day',
                                          stock_symbol=None)

# Add columns for time and 3 stock columns
table.add_column('date', 'Date', datatype='date', iskey=True)

# Bind the table to a widget for display
report.add_widget(c3.TimeSeriesWidget, table, 'Close Prices', width=12)


# Implement a widget to display the daily volumns for multiple stocks
table = stock.MultiStockVolumeTable.create(name='multi-stock-volume',
                                           duration='52w', resolution='day')
table.add_column('date', 'Date', datatype='date', iskey=True)
report.add_widget(c3.TimeSeriesWidget, table, 'Daily Volumes', width=12)
