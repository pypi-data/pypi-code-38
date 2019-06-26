"""

"""

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
        return {'TexasInstruments': texas_instruments}
    else:
        return {}


def get_auto_importers():
    return get_importers()


def texas_instruments(file):
    importer = 'TexasInstruments'
    header = dict()
    with open(file, 'r') as f:
        date = _check_header(f)
        _read_header(f, header)
        data = _read_data(f, importer)
        output = DataContainer(data, type='spectrum')
    header['Date'] = date
    output.update_header(header)
    if output.empty:
        raise utils.ImportFailed('\'{1}\' importer Did not find any valid data in file \'{0}\''.format(file, importer))
    return output


def _check_header(f):
    importer = 'TexasInstruments'
    first_start = 'Spectrum'
    second_start = '[Global Parameters]'
    try:
        line = f.readline()

        if not line.startswith(first_start):
            raise utils.UnknownFileType(
                '\'{0}\' importer: first line of file must start with \"{1}\"'.format(importer, first_start))
        date = line.split(',')[1].strip('\n')

        line = f.readline()
        if not line.startswith(second_start):
            raise utils.UnknownFileType(
                '\'{0}\' importer: first line of file must start with \"{1}\"'.format(importer, second_start))
    except UnicodeDecodeError:
        raise utils.UnknownFileType('\'{0}\' importer: cannot open file'.format(importer))
    return date


def _read_header(f, header):
    line = True
    while line:
        line = f.readline()
        _read_line(line, header)

        if line.startswith('[Traces]'):
            break


def _read_line(line, header):
    dict = {
        'Span': (_numeric, 'Span'),
        'Resolution Bandwidth': (_numeric, 'RBW'),
        'Video Bandwidth': (_numeric, 'VBW'),
        'Actual RBW': (_numeric, None),
        'Frequency': (_multiple_keyword, 'CenterFrequency'),
        'Reference Level': (_numeric, None),
    }
    split = line.split(',')
    keyword = split[0]
    try:
        function = dict[keyword][0]
        key = dict[keyword][1]
    except KeyError:
        return

    try:
        function(split, header, key)
    except Exception:
        print('Could not import line {0}'.format(line))


def _numeric(split, header, key):
    if key:
        header[key] = float(split[1])
    else:
        header.update({split[0]: float(split[1])})


def _string(split, header, key):
    if key:
        header[key] = split[1]
    else:
        header.update({split[0]: split[1]})


def _multiple_keyword(split, header, key):
    try:
        header.setdefault(key, float(split[1]))
    except ValueError:  # since split[1] could also be not a number
        pass


def _read_data(f, importer):
    traces = f.read().split('[Trace]')
    del traces[0]

    data_out = pd.DataFrame()
    ylabel = utils.get_file_basename(f.name)
    # for trace in traces:
    for ii in range(len(traces)):
        trace = traces[ii]
        try:
            lines = trace.strip().splitlines()
            # name = lines.pop(0).split(',')[0].replace(' ','')
            lines.pop(0)
            name = ylabel + '_{0}'.format(ii + 1)
            points = int(lines.pop(0).split(',')[1])
            start = float(lines.pop(0).split(',')[1])
            stop = float(lines.pop(0).split(',')[1])
            y = [float(i) for i in lines]
            x = np.linspace(start, stop, num=points)
            data = pd.DataFrame(data=y, index=x, columns=[name])
        except ValueError:
            raise utils.ImportFailed(
                '\'{2}\' importer: Number of points does not fit number of values in \'{0}\' in file \'{1}\'.'.format(
                    name, f.name, importer))
        data.index.rename('Frequency', inplace=True)
        if data_out.empty:
            data_out = data
        # elif len(data_out) == len(data):
        elif (data_out.index == data.index).all():
            data_out = data_out.join(data)
        else:
            raise utils.ImportFailed(
                '\'{1}\' importer: Traces in file \'{0}\' do not have equal frequency axis.'.format(f.name, importer))
    return data_out
