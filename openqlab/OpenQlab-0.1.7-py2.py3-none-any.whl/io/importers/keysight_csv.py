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
        return {'KeysightCSV': keysight_csv}
    else:
        return {}


def get_auto_importers():
    return get_importers()


def keysight_csv(file):
    importer = 'KeysightCSV'
    with open(file, 'r') as f:
        _check_header(f, importer)
        # _read_header(f, header, importer)
        data = _read_data(f)
        output = DataContainer(data, type='osci')
        output.header['xUnit'] = 's'
        output.header['yUnit'] = 'V'
    if output.empty:
        raise utils.ImportFailed('\'{1}\' importer Did not find any valid data in file \'{0}\''.format(file, importer))
    return output


def _check_header(f, importer):
    first_start = 'x-axis'
    second_start = 'second'
    try:
        line = f.readline()
        if not line.startswith(first_start):
            raise utils.UnknownFileType(
                '\'{0}\' importer: first line of file must start with \'{1}\''.format(importer, first_start))

        line = f.readline()
        if not line.startswith(second_start):
            raise utils.UnknownFileType(
                '\'{0}\' importer: first line of file must start with \'{1}\''.format(importer, second_start))
    except UnicodeDecodeError:
        raise utils.UnknownFileType('\'{0}\' importer: cannot open file'.format(importer))


def _read_data(f):
    xlabel = 'Time'
    ylabel = utils.get_file_basename(f.name)
    output = pd.read_csv(f, sep=',', index_col=0, prefix=ylabel + '_', header=None)
    output.index.name = xlabel
    return output
