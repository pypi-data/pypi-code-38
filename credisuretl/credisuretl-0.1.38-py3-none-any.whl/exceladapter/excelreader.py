import openpyxl


class ExcelReader:
    def __init__(self, filename):
        self.workbook = openpyxl.load_workbook(filename=filename, data_only=True)

    def get_sheet(self, sheetname):
        return self.workbook.get_sheet_by_name(sheetname)
