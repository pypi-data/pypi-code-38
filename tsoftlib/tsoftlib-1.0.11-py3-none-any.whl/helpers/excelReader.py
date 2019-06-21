from xlrd import open_workbook
import os
import re

DEFAULTEXCELPATH = './excel'

def readDir():
    l = []
    (_, _, fileList) = next(os.walk(DEFAULTEXCELPATH))
    for f in fileList:
        if re.match(r'^.*\.xlsx$', f):
            l.append(f)
    return l


def readExcel():
    excelData = {}
    for file in readDir():
        book = open_workbook(DEFAULTEXCELPATH + '/' + file)
        bookData = []
        for sheet in book.sheets():
            sheetData = []
            for row in range(1, sheet.nrows):
                col_names = sheet.row(0)
                rowData = []
                for name, col in zip(col_names, range(sheet.ncols)):
                    value = str(sheet.cell(row, col).value)
                    rowValues = {
                        "colName": name.value,
                        "rowValue": value
                    }
                    rowData.append(rowValues)                
                sheetData.append(rowData)
            bookData.append(sheetData)
        excelData[file] = bookData
    return excelData