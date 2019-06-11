class RowUnpacker:
    def __init__(self, sheet, row_num):
        self.sheet = sheet
        self.row_num = row_num

    def get_value_at(self, col):
        return self.sheet.cell(row=self.row_num, column=col).value
