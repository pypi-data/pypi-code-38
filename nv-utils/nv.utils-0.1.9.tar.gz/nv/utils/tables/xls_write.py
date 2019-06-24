import os

import xlwt

from .utils import normalize, check_normalized
from .csv import write_csv


def write_xls(data, fp, headers=None, normalize_data=True, default='', **kwargs):
    """
    Write a Python object to a XLS or XLSX file based on xlrd.
    :param filename: XLS or XLSX file
    :param headings: list of headings. If None, will compile form data.
    """
    sheet_num = 1

    if normalize_data:
        data = normalize(data, headers=headers, default=default)
    elif not check_normalized(data, headers=headers):
        raise ValueError(
            'Data must be normalized for XLS files (i.e. all dicts must have same keys). Suggestion: use normalize_data=True')

    headers = headers or list(data[0].keys())

    book = xlwt.Workbook()
    rowd = 0

    if len(data) != 0:
        while rowd < len(data):

            sheet = book.add_sheet("Sheet{}".format(sheet_num))

            rowx = 0
            rowp = 0

            for colx, value in enumerate(headers):
                sheet.write(rowx, colx, value)

            sheet.set_panes_frozen(True)  # frozen headings instead of split panes
            sheet.set_horz_split_pos(rowx+1)  # in general, freeze after last heading row
            sheet.set_remove_splits(True)  # if user does unfreeze, don't leave a split there

            for row in data[rowd:]:
                rowx += 1
                rowp += 1
                for k in row.keys():
                    sheet.write(rowx, headers.index(k), row.get(k, ""))
                if rowp > 65534:
                    break

            rowd += rowp
            sheet_num += 1

    book.save(fp)



