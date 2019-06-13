'''
This file is part of the EdTech library project at Full Sail University.

    Foobar is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Foobar is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

    Copyright (C) 2014, 2015 Full Sail University.
'''

import xlrd
import os
import csv, codecs

def deleteColumn(rowData, columnNo):
    for rowIndex in range (0, len(rowData)):
        newRow = []
        for entryIndex in range(0, len(rowData[rowIndex])):
            if entryIndex != columnNo:
                newRow.append(rowData[rowIndex][entryIndex])
        rowData[rowIndex] = newRow

def deleteColumns(rowData, columns):
    for column in reversed(columns):
        deleteColumn(rowData, column)

def getColumn(rowData, number):
    columnData = list()
    
    for row in rowData:
        columnData.append(row[number])

    return columnData

def getColumnsNum(rowData):
    columns = 0
    
    for row in rowData:
        if len(row) > columns:
            columns = len(row)

    return columns

def getExcelSheetAsCsv(workbook, sheetName = None):
    if sheetName != None:
        sheet = workbook.sheet_by_name(sheetName)
    else:
        sheet = workbook.sheet_by_index(0)

    # Get the row data
    rowData = list()
    for row in range(sheet.nrows):
        values = list()
        for col in range(sheet.ncols):
            values.append(sheet.cell(row, col).value)
        rowData.append(values)

    return rowData

def loadCsv(filename, dialect = None):
    # Determine if the file exists. If not, raise an exception.
    if not os.path.isfile(filename):
        raise Exception("Error: " + filename + " not found.")
    
    # Determine the csv file dialect (if not provided)
    csvFile = open(filename, 'rU')
    
    # Read file into list of lists
    if dialect != None:
        reader = csv.reader(csvFile, dialect)
    else:
        reader = csv.reader(csvFile)

    rowData = list()
    for row in reader:
        rowData.append(row)
    
    csvFile.close()
    return rowData

def loadExcel(filename):
    # Determine if the file exists. If not, raise an exception.
    if not os.path.isfile(filename):
        raise Exception("Error: " + filename + " not found.")
    
    # Load the workbook.
    try: workbook = xlrd.open_workbook(filename)
    except: pass

    return workbook

def loadExcelSheetAsCsv(filename, sheetName = None):
    return getExcelSheetAsCsv(loadExcel(filename), sheetName)

def saveCsv(filename, rowData, insertKey = False):
    # Open file for writing
    csvFile = codecs.open(filename, 'wb')
    writer = csv.writer(csvFile, quotechar='"', delimiter=',')

    # Write the data
    if insertKey:
        for key, row in rowData.iteritems():
            print("Key: " + key + " Value: " + row)
            writer.writerow([ key ] + row)
    else:
#       i = 0
        for row in rowData:
#            print "[" + str(i) + "]: " + row
            writer.writerow(row)

    # Close the file
    csvFile.close()

def write_multiple(sheet, rowIndex, colIndex, dataList, style):
    for cellData in dataList:
        sheet.write(rowIndex, colIndex, cellData, style)
        colIndex = colIndex + 1

# http://stackoverflow.com/questions/9574793/how-to-convert-a-python-datetime-datetime-to-excel-serial-date-number
def excel_date(date):
    delta = date - datetime.date(1899, 12, 30) # TODO: Origin date different for Mac Excel?
    return float(delta.days) + (float(delta.seconds) / 86400) # 86400 == seconds/day
