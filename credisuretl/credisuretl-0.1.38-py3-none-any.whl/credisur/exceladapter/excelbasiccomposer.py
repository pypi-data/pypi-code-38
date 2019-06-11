from . import ExcelWriter
from credisur.excelbuilder import BasicBuilder

class ExcelBasicComposer:

    def __init__(self, filename, collection, columns_configuration, sheetname):
        self.writer = ExcelWriter(filename)
        builder = BasicBuilder(collection, columns_configuration)
        self.writer.build_sheet(sheetname, builder.build_sheet_data())

    def save(self):
        self.writer.save()