import xlrd
import logging
import sys
import json

    
def read_excel_workbook(file_path):
    book = xlrd.open_workbook(file_path)
    logging.debug("The number of worksheets is {0}".format(book.nsheets))
    logging.debug("Worksheet name(s): {0}".format(book.sheet_names()))
    workbook_values = []
    num_sheets = book.nsheets
    if book.nsheets == 0:
        logging.error("No Sheets present in the file")
        return None
    for sheet_idx in range(0, num_sheets):
        min_row_id = 999999
        max_row_id = 0
        min_col_id = 999999
        max_col_id = 0

        sh = book.sheet_by_index(sheet_idx)
        for row_id in range(0, sh.nrows):
            for col_id in range(0, sh.ncols):
                if sh.cell_value(row_id, col_id) != xlrd.empty_cell.value:
                    if max_col_id < col_id:
                        max_col_id = col_id
                    if min_col_id > col_id:
                        min_col_id = col_id
                    if max_row_id < row_id:
                        max_row_id = row_id
                    if min_row_id > row_id:
                        min_row_id = row_id
        sheet_matrix = []
        for row_id in range(min_row_id, max_row_id + 1):
            row_data = sh.row_slice(row_id, min_col_id, max_col_id + 1)
            row_values = []
            for data in row_data:
                if data.value == xlrd.empty_cell.value:
                    row_values.append("")
                else:
                    row_values.append(data.value)
            sheet_matrix.append(row_values)
        workbook_values.append(sheet_matrix)
    return json.dumps(workbook_values)


def log_helper():
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)

if __name__ == "__main__":
    log_helper()
    print((read_excel_workbook('./tests/Diarrhoea.xlsx')))
