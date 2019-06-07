import datetime as dt
import pandas as pd

from dftogsheet import auth
from dftogsheet import config


class Sheet:
    # sheet.value = [
    #     ['row1col1', 'row1col2', 'row1col3'],
    #     ['row2col1', 'row2col2', 'row2col3']
    # ]

    def __init__(self, df_subsection):
        value = df_subsection.tolist()
        # Must be a two dimentional array
        if len(value) == 0:
            value = [[]]
        elif not isinstance(value[0], list):
            value = [value]
        # Each row must be the same length
        l = len(value[0])
        for i in range(0, len(value)):
            lr = len(value[i])
            if lr != l:
                raise AttributeError(f'Missing cells in table: Rown {i} has {lr} rows.')
        self.value = value

    
    def unsupported_datatypes_tostr(self):
        for i in range(len(self.value)):
            for j in range(len(self.value[i])):
                cell = self.value[i][j]
                # Google Sheets API doesn't like datestime.date or lists
                if isinstance(cell, dt.date) or isinstance(cell, list):
                    self.value[i][j] = str(cell)
                # Stringinfy np.nan, but leave None
                elif cell and pd.isnull(cell):
                    self.value[i][j] = 'NaN'
    
    def set_range(self, sheet_name=False, offset=0):
        self.range = Range(self.value, offset)
        self.range.set_str(sheet_name=sheet_name)
        return self.range

    def write(self, spreadsheet_id):
        write_value = {
            'values': self.value
        }
        service = auth.Service(config.scopes)
        gsheet = service.resource.spreadsheets()

        for i in range(0, 3):
            # This sometimes unexplainably fails, but works again on the second try.
            # Therefore I am trying 3 times before exiting the script
            # Issue details: https://github.com/googleapis/google-api-python-client/issues/632
            try:
                result = gsheet.values().update(
                    spreadsheetId=spreadsheet_id,
                    range=self.range.str,
                    valueInputOption=config.value_input_option,
                    body=write_value
                ).execute()
                print('{0} cells updated.'.format(result.get('updatedCells')))
                break
            except Exception as e:
                print(e)


class Range:
    first_row = 1
    last_row = 1
    first_col = 1
    last_col = 1
    
    def __init__(self, sheet_value, offset):
        if not isinstance(offset, int):
            raise AssertionError('offset must be int')
        self.first_row = Index(1 + offset)
        self.last_row = Index(self.first_row.value + len(sheet_value) -1)
        self.first_col = Index(1)
        self.last_col = Index(self.first_col.value + len(sheet_value[0]) -1)

    def width(self):
        return self.last_col.value - self.first_col.value + 1

    def height(self):
        return self.last_row.value - self.first_row.value + 1

    def set_str(self, sheet_name=False):
        string = ''
        if sheet_name:
            string = f'{sheet_name}!'
        fc = self.first_col.to_alph()
        lc = self.last_col.to_alph()
        fr = self.first_row.to_str()
        lr = self.last_row.to_str()
        self.str = f'{string}{fc}{fr}:{lc}{lr}'
        return self.str


class Index:
    def __init__(self, num):
        self.value = num

    # Copied from https://stackoverflow.com/questions/23861680/convert-spreadsheet-number-to-column-letter
    def to_alph(self):
        num = self.value
        string = ''
        while num > 0:
            num, remainder = divmod(num - 1, 26)
            string = chr(65 + remainder) + string
        return string
    
    def to_str(self):
        return str(self.value)
