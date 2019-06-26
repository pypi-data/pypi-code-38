from . import utils
from OpenQlab.io.data_container import DataContainer

try:
    import numpy as np
    import pandas as pd

    has_imports = True
except ImportError:
    has_imports = False


def get_importers():
    if has_imports:
        return {'DataContainerCSV': data_container_csv}
    else:
        return {}


def get_auto_importers():
    return get_importers()


def data_container_csv(file):
    importer = 'DataContainerCSV'
    header = dict()
    with open(file, 'r') as f:
        _check_header(f, importer)
    output = DataContainer.from_csv(file, parse_dates=True)
    if output.empty:
        raise utils.ImportFailed('\'{1}\' importer Did not find any valid data in file \'{0}\''.format(file, importer))
    return output


def _check_header(f, importer):
    first_line = DataContainer.json_prefix
    try:
        line = f.readline()
        if not line.startswith(first_line):
            raise utils.UnknownFileType(
                '\'{0}\' importer: first line of file must start with \'{1}\''.format(importer, first_line))

    except UnicodeDecodeError:
        raise utils.UnknownFileType('\'{0}\' importer: cannot open file'.format(importer))
