from .rowunpacker import *


class TableUnpacker:
    def __init__(self, sheet):
        self.sheet = sheet

    def get_row_unpacker(self, row):
        return RowUnpacker(self.sheet, row)

    def get_value_at(self, row, col):
        return self.sheet.cell(row=self.rowNum, column=col).value

    def read_rows(self, initial_row):
        for row_num in range(initial_row, self.sheet.max_row + 1):
            yield self.get_row_unpacker(row_num)
