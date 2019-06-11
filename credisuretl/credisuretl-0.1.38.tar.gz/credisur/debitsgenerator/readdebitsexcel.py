import openpyxl

def read_debits_excel(excel_path):
    workbook = openpyxl.load_workbook(
        filename=excel_path, read_only=True, data_only=True)
    # workbook.get_sheet_by_name(sheetname)

    mapper_func = sheet_builder(workbook)
    bank_sheets = map(mapper_func, list(filter(is_bank_sheet, workbook.sheetnames)))

    return bank_sheets


def is_bank_sheet(sheet_name):
    return sheet_name.startswith("Banco")

def sheet_builder(workbook):
    def mapper(sheetname):
        return workbook.get_sheet_by_name(sheetname)

    return mapper