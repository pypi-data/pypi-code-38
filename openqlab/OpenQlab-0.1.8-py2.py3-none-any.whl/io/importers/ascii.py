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
        return {'ASCII': ascii,
                'Flipper': ascii,
                'SR785': ascii}
    else:
        return get_importers()


def get_auto_importers():
    return get_importers()


def ascii(file, sep='\t'):
    importer = 'ASCII'
    _check_header(file, importer)
    data = _read_data(file, sep)
    output = DataContainer(data)
    if output.empty:
        raise utils.ImportFailed('\'{1}\' importer Did not find any valid data in file \'{0}\''.format(file, importer))
    return output


def _check_header(file, importer):
    with open(file, 'r') as f:
        for ii in range(11):
            try:
                line = f.readline()
            except UnicodeDecodeError:
                raise utils.UnknownFileType(
                    '\'{0}\' importer: cannot decode binary file'.format(importer))

            list = line.split()
            for item in list:
                try:
                    float(item)
                except ValueError:
                    raise utils.UnknownFileType(
                        '\'{0}\' importer: expected plain numeric ASCII'.format(importer))


def _read_data(file, sep):
    xlabel = 'x'
    ylabel = utils.get_file_basename(file)
    data = pd.read_csv(file, sep=sep, index_col=0, usecols=[0, 1],
                       names=[xlabel, ylabel], header=None, engine='python')
    return data
