import credisur.exceladapter as exceladapter
from . import TableUnpacker


class DataExtractor:

    # TODO: separar contexto de results

    def __init__(self, filename, sheetname, results_initialization, extract_row, initial_row = 2):
        reader = exceladapter.excelreader.ExcelReader(filename)
        sheet = reader.get_sheet(sheetname)

        self.unpacker = TableUnpacker(sheet)
        self.results = results_initialization
        self.extract_row = extract_row
        self.initial_row = initial_row

    def extract(self):
        for row_unpacker in self.unpacker.read_rows(self.initial_row):
            self.extract_row(self.results, row_unpacker)

        return self.results
