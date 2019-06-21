import xlsxwriter
import json
from dicttoxml import dicttoxml
from .fileMaker import makeFolderIfNotExists

DEFAULTOUTPUTPATH = './output'

# filename[str] | data[list of dict] -> colsname / values
def PrintToExcel(fileName, data):
    makeFolderIfNotExists(DEFAULTOUTPUTPATH)
    workbook = xlsxwriter.Workbook(f'{DEFAULTOUTPUTPATH}/{fileName}.xlsx')
    worksheet = workbook.add_worksheet('1')

    row = 0
    col = 0

    colNames = data[0].keys()

    # Write ColumnNames to First Row of sheet
    for names in colNames:
        worksheet.write(row, col, names)
        col += 1

    col = 0
    row += 1

    for item in data:
        for index, name in enumerate(colNames):
            try:
                worksheet.write(row, index, item[name])
            except:
                worksheet.write(row, index, '')

        row += 1

    workbook.close()

 
def PrintToJson(fileName, data):
    makeFolderIfNotExists(DEFAULTOUTPUTPATH)
    with open(f'{DEFAULTOUTPUTPATH}/{fileName}.json', 'w+') as file:
        file.write(json.dumps(data))
        file.close()

def PrintToXML(fileName, data):
    makeFolderIfNotExists(DEFAULTOUTPUTPATH)
    with open(f'{DEFAULTOUTPUTPATH}/{fileName}.xml', 'w+') as file:
        file.write(dicttoxml(data).decode('UTF-8'))
        file.close()
