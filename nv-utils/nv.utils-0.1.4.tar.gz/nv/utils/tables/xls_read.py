import xlrd

from .csv import write_csv


def convert_sheet(workbook, sheet=None, formatting_info=False, float_to_int=True, empty_value=None):

    if sheet is None:
        wks = workbook.sheet_by_index(0)
    else:
        wks = workbook.sheet_by_name(sheet)

    # Reads first row
    first_row = list()
    for col in range(wks.ncols):
        first_row.append(wks.cell_value(0, col))

    data = list()
    for row in range(1, wks.nrows):
        elm = {}
        for col in range(wks.ncols):
            value = wks.cell_value(row, col)
            value = value if value != '' else empty_value
            if float_to_int and type(value) == float and int(value) == value:
                value = int(value)
            if formatting_info and wks.cell_xf_index(row, col) == xlrd.XL_CELL_DATE:
                elm[first_row[col]] = xlrd.xldate_as_tuple(value, workbook.datemode)
            else:
                elm[first_row[col]] = value
        data.append(elm)

    return data


def read_xls(fp, sheet=None, empty_value=None, **kwargs):
    """
    Read a Python object from a XLS or XLSX file based on xlrd
    :param filename: XLS or XLSX file
    :param sheet: Sheet name (defaults to first spreadsheet)
    :param kwargs:
    :return: Python object
    """
    if type(fp) is str:
        kwargs.update({'filename': fp,
                       'file_contents': None})
    else:
        kwargs.update({'file_contents': fp,
                       'filename': None})

    try:
        wkb = xlrd.open_workbook(formatting_info=True, **kwargs)
        formatting_info = True
    except NotImplementedError:
        # Catches formatting_info not implemented for 2007 Excel (.xlsm) files
        wkb = xlrd.open_workbook(**kwargs)
        formatting_info = False

    return convert_sheet(wkb, sheet=sheet, formatting_info=formatting_info, empty_value=empty_value)


def xls_to_csv(xls_file, csv_folder, ignore_dashed_names=True):

    wkb = xlrd.open_workbook(xls_file)
    sheet_names = wkb.sheet_names()

    for sheet_name in sheet_names:
        if ignore_dashed_names and sheet_name.startswith('_'):
            continue
        data = convert_sheet(wkb, sheet=sheet_name)
        file_name = os.path.join(csv_folder, sheet_name + '.csv')
        write_csv(data, file_name)
