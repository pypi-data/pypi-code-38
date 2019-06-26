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
        return {'Gwinstek': gwinstek}
    else:
        return {}


def get_auto_importers():
    return get_importers()


def gwinstek(file):
    importer = 'Gwinstek'
    header = dict()
    with open(file, 'r') as f:
        _check_header(f, header, importer)
        _read_header(f, header, importer)
        data = _read_data(f, header, importer)
        output = DataContainer(data, type='osci')

    output.update_header(header)
    if output.empty:
        raise utils.ImportFailed('\'{1}\' importer: Did not find any valid data in file \'{0}\''.format(file, importer))
    return output


def _check_header(f, header, importer):
    first_start = 'Format,1.0B'
    second_start = 'Memory Length'
    try:
        line = f.readline()
        if not line.startswith(first_start):
            raise utils.UnknownFileType(
                '\'{0}\' importer: first line of file must start with \'{1}\''.format(importer, first_start))

        line = f.readline()

        if not line.startswith(second_start):
            raise utils.UnknownFileType(
                '\'{0}\' importer: first line of file must start with \'{1}\''.format(importer, second_start))
        split = line.split(',')
        num_traces = int((len(split)) / 2)
        num_points = int(split[1])
        header.update({'NumTraces': num_traces, 'NumPoints': num_points})
    except UnicodeDecodeError:
        raise utils.UnknownFileType('\'{0}\' importer: cannot open file'.format(importer))


def _read_header(f, header, importer):
    line = True
    while line:
        line = f.readline()
        if line.startswith('Waveform Data'):
            break
        _read_line(line, header, importer)


def _read_line(line, header, importer):
    dict = {
        'Source': (_string, None),
        'Vertical Units': (_string, 'yUnit'),
        'Vertical Units Div': (_numeric, None),
        'Vertical Units Extend Div': (_numeric, None),
        'Label': (_string, None),
        'Probe Type': (_numeric, None),
        'Probe Ratio': (_numeric, None),
        'Vertical Scale': (_numeric, 'yScale'),
        'Vertical Position': (_numeric, 'yPosition'),
        'Horizontal Units': (_string, 'xUnit'),
        'Horizontal Scale': (_numeric, 'xScale'),
        'Horizontal Position': (_numeric, 'xOffset'),
        'SincET Mode': (_string, None),
        'Sampling Period': (_numeric, None),
        'Horizontal Old Scale': (_numeric, None),
        'Horizontal Old Position': (_numeric, None),
        'Firmware': (_string, None),
        'Mode': (_string, None),
    }
    try:
        split = line.split(',')
        (keyword, value) = split[0], split[1]
    except ValueError:
        raise utils.UnknownFileType('\'{0}\' importer: line does not match expected format.'.format(importer))

    try:
        function = dict[keyword][0]
        key = dict[keyword][1]
    except KeyError:
        return

    try:
        function(header, key, keyword, value)
    except Exception:
        print('Could not import line {0}'.format(line))


def _numeric(header, key, keyword, value):
    if key:
        header[key] = float(value)
    else:
        header.update({keyword: float(value)})


def _string(header, key, keyword, value):
    if key:
        header[key] = value
    else:
        header.update({keyword: value})


def _read_data(f, header, importer):
    xlabel = 'Time'
    file = f.name
    try:
        mode = header['Mode']
        num_traces = header['NumTraces']
        num_points = header['NumPoints']
        x_offset = header['xOffset']
        start = - header['xScale'] / 2 + x_offset
        stop = header['xScale'] / 2 + x_offset
    except KeyError:
        raise utils.ImportFailed(
            '\'{1}\' importer: could not determine save mode in file \'{0}\''.format(file, importer))

    ylabel = utils.get_file_basename(f.name)
    ylabels = [ylabel + '_{0}'.format(ii) for ii in range(1, num_traces + 1)]
    if mode == 'Detail':
        names = [xlabel] + ylabels
        usecols = [0, 1] + list(range(3, 2 * num_traces + 1, 2))
        output = pd.read_csv(f, sep=',', index_col=0, usecols=usecols,
                             names=names, header=None)
    elif mode == 'Fast':
        names = ylabels
        usecols = list(range(0, 2 * num_traces - 1, 2))
        x = np.linspace(start, stop, num=num_points)
        output = pd.read_csv(f, sep=',', usecols=usecols,
                             names=names, header=None, skipinitialspace=True)
        output.index = x
        output.index.name = xlabel
    else:
        raise utils.ImportFailed(
            '\'{1}\' importer: expected save modes \"Detail\" or \"Fast\" not found in file \'{0}\''.format(file,
                                                                                                            importer))
    return output
