name = "dftogsheet"

from dftogsheet.auth import *
from dftogsheet.config import Config
from dftogsheet.sheet import *


def write_to_sheet(df, spreadsheet_id, sheet_name):
    config = Config()

    # Headers
    headers = sheet.Sheet(df.columns)
    headers.unsupported_datatypes_tostr()
    headers.set_range(sheet_name=sheet_name)
    headers.overwrite(spreadsheet_id, config)

    # Body
    body = sheet.Sheet(df.values)
    body.unsupported_datatypes_tostr()
    body.set_range(sheet_name=sheet_name, offset=1)
    body.write(spreadsheet_id, config)
    