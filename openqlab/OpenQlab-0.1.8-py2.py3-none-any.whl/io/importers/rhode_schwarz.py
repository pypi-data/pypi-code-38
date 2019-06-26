from . import utils
from OpenQlab.io.data_container import DataContainer
import re

try:
    import numpy as np
    import pandas as pd

    has_imports = True
except ImportError:
    has_imports = False

my_name = 'RhodeSchwarz'

def get_importers():
    if has_imports:
        return {my_name: rhode_schwarz}
    else:
        return {}

def get_auto_importers():
    return get_importers()


def rhode_schwarz(file):
    with open(file, 'r') as f:
        _check_header(f)
        f.seek(0)
        header, data = _parse_file(f)

    output = DataContainer(data, type='spectrum')
    output.update_header(header)
    if output.empty:
        raise utils.ImportFailed(f'{my_name}: Did not find any valid data in file "{file}"')
    return output


def _check_header(f):
    first_start = 'Type'
    second_start = 'Version'
    try:
        line = f.readline()
        if not line.startswith(first_start):
            raise utils.UnknownFileType(f'{my_name}: first line of file must start with "{first_start}"')
        model = line.split(';')[1]
        line = f.readline()
        if not line.startswith(second_start):
            raise utils.UnknownFileType(f'{my_name}: second line of file must start with "{second_start}"')
        return model
    except UnicodeDecodeError:
        raise utils.UnknownFileType(f'{my_name}: cannot open file')

def _numeric(header, key, keyword, value, unit):
    if key:
        header[key] = float(value)
    else:
        if unit:
            header.update({keyword: (float(value), unit.strip())})
        else:
            header.update({keyword: float(value)})


def _string(header, key, keyword, value, unit):
    if key:
        header[key] = value
    else:
        header.update({keyword: value})


def _get_xlabel(header):
    try:
        x_unit = header['xUnit']
        if x_unit == 's':
            xlabel = 'Time'
        elif x_unit == 'Hz':
            xlabel = 'Frequency'
        else:
            xlabel = 'x'
    except KeyError:
        xlabel = 'x'

    return xlabel

header_map = {
    'RBW': (_numeric, 'RBW'),
    'VBW': (_numeric, 'VBW'),
    'Center Freq': (_numeric, 'CenterFrequency'),
    'Span': (_numeric, 'Span'),

    'Start': (_numeric, None),
    'Stop': (_numeric, None),
    'SWT': (_numeric, None),
    'Ref Level': (_numeric, None),
    'Level Offset': (_numeric, None),
    'Rf Att': (_numeric, None),
    'Sweep Count': (_numeric, None),
    'Values': (_numeric, None),

    'x-Axis': (_string, None),
    'y-Axis': (_string, None),
    'Trace Mode': (_string, None),
    'Detector': (_string, None),
    'x-Unit': (_string, 'xUnit'),
    'y-Unit': (_string, 'yUnit'),
    'Preamplifier': (_string, None),
    'Transducer': (_string, None),
    'Mode': (_string, None),
    'Date': (_string, 'Date'),
}
def _parse_file(f):
    header = {}
    data = []
    current_trace = 0
    line = f.readline()
    while line:
        (keyword, value, unit) = line.strip().split(';')
        match = re.match('Trace ([\d])', keyword)
        if match:
            current_trace = match[1]

        try:
            func = header_map[keyword][0]
            mapping = header_map[keyword][1]
        except KeyError:
            line = f.readline()
            continue

        func(header, mapping, keyword, value, unit)

        # this is where the data starts
        if keyword == 'Values':
            fpos = f.tell()
            ylabel = utils.get_file_basename(f.name) + '_' + current_trace
            data.append(pd.read_csv(f, sep=';', index_col=0,
                usecols=[0, 1], names=[_get_xlabel(header), ylabel],
                header=None, nrows=header['Values']))
            f.seek(fpos)
            skip_rows = header['Values']
            while skip_rows:
                line = f.readline()
                skip_rows -= 1
        line = f.readline()
    
    data = pd.concat(data, axis=1)
    return header, data
