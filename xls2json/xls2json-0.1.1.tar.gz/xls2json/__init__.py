__version__ = '0.1.1'

import argparse
import json
import os
import xlrd
from datetime import datetime
# TODO auto detect cell type and write accordingly.
# TODO handle XLS file with no table headers.
# TODO handle non unique sheet names.
def set_args():
    args = argparse.ArgumentParser()
    args.add_argument('--perentry', action='store_true', help='Output a JSON file per entry of XLS file.')
    args.add_argument('--persheet', action='store_true', help='Output a JSON file per sheet of XLS file.')
    args.add_argument('xls_input', help='Specify XLS file.')
    args.add_argument('output_path', nargs='?', help='Specify output folder for --persheet mode.', default='output')
    return args.parse_args()

def standard_path(apath):
    try:
        if apath.endswith('/'):
            return apath
        else:
            return apath+'/'
    
    except IndexError:
        return apath
    
def per_sheet():
    '''
    Read XLS file and write each sheet to a JSON file.
    The JSON key will be the row number.
    '''
    output_path = standard_path(args.output_path)
    os.makedirs(output_path, exist_ok=1)

    book = xlrd.open_workbook(args.xls_input)
    data = {}
    
    file_name = args.xls_input

    for sheet in book.sheets():

        if file_name.endswith('x'):
            prefix = output_path+args.xls_input[:-5]+f'_{sheet.name}'
        else:
            prefix = output_path+args.xls_input[:-4]+f'_{sheet.name}'

        nb_row = max(0, sheet.nrows)
        nb_col = max(0, sheet.ncols)

        for i in range(1, nb_row):            
            number = sheet.cell_value(rowx=i, colx=0)
            helper_dict = {}

            for j in range(0, nb_col):                
                key = sheet.cell_value(rowx=0, colx=j)
                value = sheet.cell_value(rowx=i, colx=j)

                if key.startswith('tgl'):
                    value = datetime(*xlrd.xldate_as_tuple(value, book.datemode))
                    value = str(value)[:-9]
                
                helper_dict[key] = value
                data[number] = helper_dict
        
        # Save after finished reading a sheet.
        json_outfile = prefix+'.json'
        with open(json_outfile, 'w', encoding='utf-8') as outfile:
            json.dump(data, outfile, ensure_ascii=False, indent=2)

def per_entry():
    '''
    Read XLS file and write each row to a JSON file.
    The JSON key will be the row number.
    '''
    output_path = standard_path(args.output_path)
    os.makedirs(output_path, exist_ok=1)

    book = xlrd.open_workbook(args.xls_input)    
    
    for sheet in book.sheets():
        file_name = args.xls_input 
        
        if file_name.endswith('x'):
            prefix = output_path+args.xls_input[:-5]
        else:
            prefix = output_path+args.xls_input[:-4]

        nb_row = max(0, sheet.nrows)
        nb_col = max(0, sheet.ncols)

        for i in range(1, nb_row):            
            number = sheet.cell_value(rowx=i, colx=0)
            data = {}
            helper_dict = {}

            for j in range(0, nb_col):                
                key = sheet.cell_value(rowx=0, colx=j)
                value = sheet.cell_value(rowx=i, colx=j)

                if key.startswith('tgl'):
                    value = datetime(*xlrd.xldate_as_tuple(value, book.datemode))
                    value = str(value)[:-9]

                helper_dict[key] = value
                data[number] = helper_dict

            # Save after finished reading row (i)
            json_outfile = prefix+f'_{sheet.name}{i}.json'
            with open(json_outfile, 'w', encoding='utf-8') as outfile:
                json.dump(data, outfile, ensure_ascii=False, indent=2)

def single_json():
    '''
    Read XLS file and write to single JSON file.
    The JSON key will be the name of the sheet.
    '''
    if args.output_path == 'output':
        json_outfile = args.output_path+'.json'
    
    file_name = args.xls_input 

    if file_name.endswith('x'):
        json_outfile = args.xls_input[:-5]+'.json'
    else:
        json_outfile = args.xls_input[:-4]+'.json'

    book = xlrd.open_workbook(args.xls_input)
    bind = {}
    data = {}
    
    for sheet in book.sheets():
        nb_row = max(0, sheet.nrows)
        nb_col = max(0, sheet.ncols)

        for i in range(1, nb_row):            
            number = sheet.cell_value(rowx=i, colx=0)
            helper_dict = {}

            for j in range(0, nb_col):                
                key = sheet.cell_value(rowx=0, colx=j)
                value = sheet.cell_value(rowx=i, colx=j)

                if key.startswith('tgl'):
                    value = datetime(*xlrd.xldate_as_tuple(value, book.datemode))
                    value = str(value)[:-9]

                helper_dict[key] = value

            data[number] = helper_dict

        bind[sheet.name] = data
    
    # Save after finished reading everything.
    with open(json_outfile, 'w', encoding='utf-8') as outfile:
        json.dump(bind, outfile, ensure_ascii=False, indent=2)

# Usage:
# xls2json --perentry excel_file.xlsx
# xls2json --persheet excel_file.xlsx
# xls2json excel_file.xlsx

args = set_args()

def main():
    if args.perentry:
        per_entry()
    elif args.persheet:
        per_sheet()
    else:
        single_json()
