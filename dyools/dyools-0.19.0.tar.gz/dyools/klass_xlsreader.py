from __future__ import (absolute_import, division, print_function, unicode_literals)

import os

import xlrd
from past.builtins import basestring

from .klass_date import Date
from .klass_table import Table


class XlsReader(object):
    def __init__(self, *args, **kwargs):
        first_item = args[0] if len(args) > 0 else False
        second_item = args[1] if len(args) > 1 else False
        if isinstance(first_item, basestring):
            self.filename = first_item
        else:
            self.filename = kwargs.get('filename', 'File_%s.xlsx' % Date(fmt=Date.DATETIME_HASH_FORMAT))
        if isinstance(second_item, basestring):
            self.sheets = second_item.split(';')
        else:
            self.sheets = kwargs.get('sheets', [])
        if not self.sheets:
            self.sheets = []
        if not isinstance(self.sheets, list):
            self.sheets = [self.sheets]
        self.data = {}
        self.right_bottom = kwargs.get('right_bottom', False)
        self.options = kwargs.get('options', dict(formatting_info=True))

    def _nomalize_sheets(self, sheets):
        if sheets:
            if isinstance(sheets, basestring):
                sheets = sheets.split(';')
        if not isinstance(sheets, list):
            sheets = []
        if not sheets:
            sheets = []
        return sheets

    def _set_fix_merged(self, sheet):
        for row_start, row_stop, col_start, col_stop in sheet.merged_cells:
            value = sheet.cell_value(row_start, col_start)
            for i in range(row_start, row_stop):
                self.data[sheet.name]['content'].setdefault(i, {})
                for j in range(col_start, col_stop):
                    self.data[sheet.name]['content'][i][j] = value

    def _set_content(self, sheet):
        for i in range(sheet.nrows):
            self.data[sheet.name]['content'].setdefault(i, {})
            for j in range(sheet.ncols):
                self.data[sheet.name]['content'][i].setdefault(j, sheet.cell_value(i, j))

    def _detect_bounds(self, name):
        def is_empty(v):
            if isinstance(v, basestring):
                v = v.strip()
            if not v:
                return True
            else:
                return False

        def find_bounds(name, i, j):
            row_start, col_start, = i, j
            while True:
                i += 1
                if i == self.data[name]['nrows']:
                    break
                value = self.data[name]['content'][i][j]
                if is_empty(value):
                    break
            row_stop = i - 1
            i = row_start
            while True:
                j += 1
                if j == self.data[name]['ncols']:
                    break
                value = self.data[name]['content'][i][j]
                if is_empty(value):
                    break
            col_stop = j - 1
            return row_start, row_stop, col_start, col_stop

        def reserved(name, i, j):
            bounds = self.data[name]['bounds']
            for row_start, row_stop, col_start, col_stop in bounds:
                if i >= row_start and i <= row_stop and j >= col_start and j <= col_stop:
                    return True
            return False

        for i, i_values in self.data[name]['content'].items():
            for j, value in self.data[name]['content'][i].items():
                if not value and self.right_bottom:
                    if i < len(self.data[name]['content']) - 1 and j < len(self.data[name]['content'][i]) - 1:
                        if self.data[name]['content'][i + 1][j] and self.data[name]['content'][i][j + 1]:
                            value = True
                if value and not reserved(name, i, j):
                    row_start, row_stop, col_start, col_stop = find_bounds(name, i, j)
                    self.data[name]['bounds'].append((row_start, row_stop, col_start, col_stop))

    def _fill_tables(self, name):
        for row_start, row_stop, col_start, col_stop in self.data[name]['bounds']:
            table = []
            for i in range(row_start, row_stop + 1):
                table.append([self.data[name]['content'][i][j] for j in range(col_start, col_stop + 1)])
            self.data[name]['tables'].append(Table(table))

    def read(self, sheets=[], filename=False):
        filename = filename or self.filename
        sheets = sheets or self.sheets
        sheets = self._nomalize_sheets(sheets)
        book = xlrd.open_workbook(self.filename, **self.options)
        sheets = sheets or [x.name for x in book.sheets()]
        sheets = [x.name for x in book.sheets() if x.name in sheets]
        assert filename, "Please provide a filename"
        assert os.path.isfile(filename), "The file [%s] is not found" % filename
        assert sheets, "Please correct the sheet filenames"
        self.sheets = sheets
        self.filename = filename
        for sheet_name in self.sheets:
            sheet = book.sheet_by_name(sheet_name)
            self.data.setdefault(sheet_name, {})
            self.data[sheet_name].setdefault('tables', [])
            self.data[sheet_name].setdefault('bounds', [])
            self.data[sheet_name].setdefault('content', {})
            self.data[sheet_name].setdefault('ncols', sheet.ncols)
            self.data[sheet_name].setdefault('nrows', sheet.nrows)
            self._set_content(sheet)
            self._set_fix_merged(sheet)
        book.release_resources()
        for sheet_name in self.sheets:
            self._detect_bounds(sheet_name)
            self._fill_tables(sheet_name)

    def get_data(self, sheets=[]):
        sheets = self._nomalize_sheets(sheets)
        if not self.data:
            self.read(sheets=sheets)
        tables = {}
        for sheet_name, sheet_data in self.data.items():
            if not sheets or sheet_name in sheets:
                tables[sheet_name] = self.data[sheet_name]['content']
        return tables

    def get_tables(self, sheets=[]):
        sheets = self._nomalize_sheets(sheets)
        if not self.data:
            self.read(sheets=sheets)
        tables = {}
        for sheet_name, sheet_data in self.data.items():
            if not sheets or sheet_name in sheets:
                tables[sheet_name] = self.data[sheet_name]['tables']
        return tables
