"""
Helpers to load and save Python objects to different file formats.
"""

# Works out of the box with Python dependencies
from importlib.util import find_spec

from .csv import read_csv, write_csv, walk_through_csv
from .utils import *

# Check if dependencies are installed - if so, import
if find_spec('xlrd'):
    from .xls_read import read_xls, xls_to_csv

else:
    def read_xls(*args, **kwargs):
        raise ModuleNotFoundError(f'Missing package: xlrd')

    def xls_to_csv(*args, **kwargs):
        raise ModuleNotFoundError(f'Missing package: xlrd')

if find_spec('xlwt'):
    from .xls_write import write_xls
else:
    def write_xls(*args, **kwargs):
        raise ModuleNotFoundError(f'Missing package: xlwt')

if find_spec('openpyxl'):
    from .xlsx import read_xlsx, write_xlsx
else:
    def read_xlsx(*args, **kwargs):
        raise ModuleNotFoundError(f'Missing package: openpyxl')

    def write_xlsx(*args, **kwargs):
        raise ModuleNotFoundError(f'Missing package: openpyxl')
