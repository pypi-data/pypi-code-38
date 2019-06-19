# Copyright (c) 2013, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""Backends for writing to Excel"""
import os.path
import sys
import collections

from xlrd import open_workbook
from xlwt import easyxf
import xlutils.copy

from sympathy.api.exceptions import SyNodeError, SyDataError

# Only import the com client interface if running windows
if sys.platform == 'win32':
    import win32com.client as win32


class ExcelSheetBackend(object):
    def __init__(self, sheet_name):
        self._sheet_name = sheet_name

    def sheet(self):
        raise NotImplementedError("Override!")

    def set_cell_value(self, row, col, value):
        raise NotImplementedError("Override!")

    def set_cell_formatting(self, row, col, datacolumn_name,
                            offset, formatting):
        raise NotImplementedError("Override!")

    def set_cell_link(self, row, col, value):
        raise NotImplementedError("Override!")

    def insert_rows(self, begin_row, end_row):
        raise NotImplementedError("Override!")

    def write(self):
        raise NotImplementedError("Override!")

    def close(self):
        """Close sheet"""
        raise NotImplementedError("Override!")


class ExcelSheetBackendCOM(ExcelSheetBackend):
    def __init__(self, fq_report_filename, sheet_name, visible=True):
        super(ExcelSheetBackendCOM, self).__init__(sheet_name)
        self._sheet_name = sheet_name
        self._report = win32.gencache.EnsureDispatch('Excel.Application')
        self._wb = self._report.Workbooks.Open(
            os.path.abspath(fq_report_filename))
        self._report.Visible = visible
        self._ws = self._wb.Worksheets(sheet_name)
        self._alphabet = [''] + map(chr, range(65, 91))

    def sheet(self):
        return self._sheet_name

    def set_cell_value(self, row, col, value):
        cell = self._cell(row, col)
        cell.Value = value

    def set_cell_color(self, row, col, color_name, formatting_row=0):
        cell = self._cell(row, col)
        if formatting_row > 0:
            formatting_row_chrs = (
                self._xl_row_col_to_chrs(formatting_row - 1, col))
            self._report.Sheets(self._sheet_name).Select()
            self._report.Range(formatting_row_chrs).Select()
            self._report.Selection.Copy()
            self._report.Range(
                self._xl_row_col_to_chrs(row, col)).Select()
            self._report.Selection.PasteSpecial(
                Paste=win32.constants.xlPasteFormats)

        if "red" == color_name:
            cell.Interior.ColorIndex = 45
        elif "green" == color_name:
            cell.Interior.ColorIndex = 35
        elif "yellow" == color_name:
            cell.Interior.ColorIndex = 36
        else:
            cell.Interior.ColorIndex = 0

    def set_cell_formatting(self, row, col, datacolumn_name,
                            offset, formatting, formatting_row=0):
        cell = self._cell(row, col)
        if formatting_row > 0:
            formatting_row_chrs = (
                self._xl_row_col_to_chrs(formatting_row - 1, col))
            self._report.Range(formatting_row_chrs).Select()
            self._report.Selection.Copy()
            self._report.Range(
                self._xl_row_col_to_chrs(row, col)).Select()
            self._report.Selection.PasteSpecial(
                Paste=win32.constants.xlPasteFormats)
        if 'color' in formatting:
            self._apply_color_formatting(
                row, cell, datacolumn_name, offset, formatting['color'])

    def set_cell_link(self, row, col, value):
        cell = self._cell(row, col)
        self._ws.Hyperlinks.Add(cell, value)

    def insert_rows(self, begin_row, end_row):
        r = self._ws.Range("%s:%s" % (begin_row, end_row))
        r.Insert()

    def write(self):
        try:
            self._wb.Save()
        except:
            raise SyNodeError(
                "Cannot save because Workbook %s is already open. "
                "Close %s and re-execute node." % (
                    self._wb.Name, self._wb.Name))

    def close(self):
        self._wb.Close(False)

    def _cell(self, row, col):
        """Using Cell(0, 0) as the first cell. Needs to add one
        to row and col when using COM cause first cell is (1,1).
        """
        return self._ws.Cells(row + 1, col + 1)

    def _xl_row_col_to_chrs(self, row, col):
        return '%s%i' % (self._xl_col_index_to_chrs(col),
                         row + 1)

    def _xl_col_index_to_chrs(self, col_index):
        alphabet_letter_count = len(self._alphabet) - 1
        return '%s%s' % (self._alphabet[col_index / alphabet_letter_count],
                         self._alphabet[col_index % alphabet_letter_count + 1])

    def _apply_color_formatting(self, row, cell, datacolumn_name,
                                offset, color_formatting):
        if datacolumn_name in color_formatting:
            item_color = color_formatting[datacolumn_name]['list'][offset]
            if "red" == item_color:
                cell.Interior.ColorIndex = 45
            elif "green" == item_color:
                cell.Interior.ColorIndex = 35
            else:
                cell.Interior.ColorIndex = 36


class ExcelSheetBackendXLWT(ExcelSheetBackend):
    def __init__(self, fq_report_filename, sheet_name, visible=True):
        super(ExcelSheetBackendXLWT, self).__init__(sheet_name)
        self._fq_report_filename = fq_report_filename
        self._sheet_name = sheet_name
        self._rb = open_workbook(fq_report_filename)
        self._rs = self._rb.sheet_by_name(self._sheet_name)
        self._wb = xlutils.copy.copy(self._rb)
        sheet_index = self._rb.sheet_names().index(self._sheet_name)
        self._ws = self._wb.get_sheet(sheet_index)

        if self._ws.get_name() != self._sheet_name:
            raise SyDataError("Sheet name doesn't match loaded sheet name")

        # self._style_list = get_xlwt_style_list(self._rb)
        # HACK(alexader): This solution is order dependent and not good
        # If cell formatting is applied first it will not work
        # Need to store all written values to get cell formatting to work
        self._written_values = collections.defaultdict(dict)

    def sheet(self):
        return self._sheet_name

    def set_cell_value(self, row, col, value):
        self._ws.write(row, col, value)
        self._written_values[row][col] = value

    def set_cell_color(self, row, col, color_name, formatting_row=0):
        cell_color = easyxf(
            "pattern: pattern solid, fore_color %s;" % color_name)

        try:
            value = self._written_values[row][col]
        except:
            value = None
        self._ws.write(row, col, value, cell_color)

    def set_cell_formatting(self, row, col, datacolumn_name,
                            offset, formatting, formatting_row=0):
        if 'color' in formatting:
            cell_style = self._cell_color_formatting(
                datacolumn_name, offset, formatting['color'])
            if cell_style is not None:
                value = None
                try:
                    value = self._written_values[row][col]
                except:
                    pass
                self._ws.write(row, col, value, cell_style)

    def set_cell_link(self, row, col, link):
        pass

    def insert_rows(self, begin_row, end_row):
        pass

    def write(self):
        self._wb.save(self._fq_report_filename)

    def close(self):
        pass

    def _cell_color_formatting(self, datacolumn_name,
                               offset, color_formatting):
        if datacolumn_name in color_formatting:
            item_color = color_formatting[datacolumn_name]['list'][offset]
            if "red" == item_color:
                return easyxf('pattern: pattern solid, fore_color red;')
            elif "green" == item_color:
                return easyxf('pattern: pattern solid, fore_color green;')
            else:
                return easyxf('pattern: pattern solid, fore_color yellow;')
        return None


def create_excel_sheet_backend_factory():
    """Returns the most compatible ExcelSheetBackend"""
    if sys.platform == 'win32':
        return ExcelSheetBackendCOM
    else:
        return ExcelSheetBackendXLWT
