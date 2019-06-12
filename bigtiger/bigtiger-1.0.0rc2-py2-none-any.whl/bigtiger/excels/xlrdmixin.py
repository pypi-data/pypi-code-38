# encoding: utf-8

'''
Created on 2014-6-17
@author: linkeddt.com
'''

from __future__ import unicode_literals

import xlrd

from bigtiger.excels import ExcelError


class XlrdMixin(object):
    excel_error_class = ExcelError
    excel_class = None

    def read_xlsx(self, file_path, sheet_index=0, start_line_number=2):

        data = xlrd.open_workbook(file_path)
        table = data.sheets()[sheet_index]
        nrows = table.nrows
        if nrows < start_line_number + 1:
            return [], None

        data_lines = []
        page_errors = []
        for i in range(start_line_number, nrows):
            row_values = table.row_values(i)
            excel = self.excel_class(row_values)
            if excel.is_valid():
                cd = excel.cleaned_data
                data_lines.append(cd)
            else:
                for field_name, error_list in excel.errors.items():
                    err = self.excel_error_class(
                        i + 1, excel.fields[field_name], error_list)
                    page_errors.append(err)
        return data_lines, page_errors
