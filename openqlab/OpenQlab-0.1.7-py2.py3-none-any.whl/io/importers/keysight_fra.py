from . import utils
from OpenQlab.io.data_container import DataContainer

#
# Keysight DSOX-3000 series oscilloscope
# Importer for frequency response analysis module
#
try:
    import numpy as np
    import pandas as pd

    has_imports = True
except ImportError:
    has_imports = False


def get_importers():
    if has_imports:
        return {'keysight_fra': keysight_fra}
    else:
        return {}


def get_auto_importers():
    return get_importers()


def keysight_fra(file):
    importer = 'KeysightFrequencyResponse'
    with open(file, 'rb') as f:
        try:
            firstline = f.readline().decode('cp1252')
        except UnicodeDecodeError:
            raise utils.UnknownFileType('\'{0}\' importer: cannot open file'.format(importer))
        if firstline.startswith('#, Frequency (Hz), Amplitude (Vpp), Gain (dB), Phase'):
            sep = ','
        elif firstline.startswith('#; Frequency (Hz); Amplitude (Vpp); Gain (dB); Phase'):
            sep = ';'
        else:
            raise utils.UnknownFileType('keysight_fra_pandas: Header line does not match expected format')

        data = pd.read_csv(f, sep=sep, index_col=0, usecols=[1, 2, 3, 4],
                           names=['Frequency (Hz)', 'Amplitude (Vpp)', 'Gain (dB)', 'Phase (deg)'],
                           header=None)
        output = DataContainer(data)
        return output
