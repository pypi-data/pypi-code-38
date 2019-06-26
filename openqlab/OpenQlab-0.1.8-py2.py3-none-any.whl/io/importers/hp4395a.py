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
        return {'HP4395A': hp4395a}
    else:
        return {}


def get_auto_importers():
    return get_importers()


def hp4395a(file):
    importer = 'HP4395A'
    channels = []
    with open(file, 'r', errors='replace') as f:
        points = 0
        channel = 0
        try:
            line = f.readline()
        except UnicodeDecodeError:
            raise utils.UnknownFileType('\'{0}\' importer: cannot open file'.format(importer))
        if not (line.startswith('"4395A') or line.startswith('"8751A')):
            raise utils.UnknownFileType(
                '{0} importer: file does not start with instrument identifier.'.format(importer))

        while line:
            line = f.readline()
            if line.startswith('"NUMBER of POINTS'):
                points = int(line.rstrip('\r\n')[19:-1])
            elif line.startswith('"CHANNEL'):
                channel = int(line.rstrip('\r\n')[10:-1])
            elif line.startswith('"Frequency"'):
                pos = f.tell()  # UGLY: pd.read_table seems to always seek to the
                #       end of the file, so store our approx.
                #       position here.
                channels.append(pd.read_table(f, index_col=0, nrows=points,
                                              names=['Frequency',
                                                     'Ch{0} Data Real'.format(channel),
                                                     'Ch{0} Data Imag'.format(channel),
                                                     'Ch{0} Mem Real'.format(channel),
                                                     'Ch{0} Mem Imag'.format(channel),
                                                     ]))
                f.seek(pos)

        if not len(channels):
            raise utils.ImportFailed('HP4395A importer: no data found')
        data = pd.concat(channels, axis=1)
        output = DataContainer(data, type='spectrum')
        return output
