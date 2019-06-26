from . import utils
from OpenQlab.io.data_container import DataContainer

import pandas as pd
import numpy as np
from scipy.io import loadmat
import xml.etree.ElementTree as ET
from io import StringIO

def get_importers():
    return {'TekSpectrogram': tek_spectrogram}
    
def get_auto_importers():
    return get_importers()

def tek_spectrogram(filename):
    importer = 'TekSpectrogram'
    with open(filename, 'rb') as f:
        _check_header(f, importer)
        header, data = _read_file(f, importer)
        output = DataContainer(data, header=header, type='spectrum')
        return output

def _check_header(f, importer):
    if f.read(6) == b'MATLAB':
        f.seek(0)
    else:
        raise utils.UnknownFileType(f'{importer}: expected first 6 bytes to read "MATLAB"')
 
def _read_file(f, importer):
    data = loadmat(f)
    requiredKeys = ['rsaMetadata', 'SpectraCenter', 'SpectraSpan', 'TDelta', 'S0']
    for key in requiredKeys:
        if not key in data.keys():
            raise utils.UnknownFileType(f"{importer}Matlab file, but don't yet know how to handle it.")

    header = _create_header(data)
    frequencies = np.linspace(header['StartFrequency'],
                              header['StopFrequency'], len(data['S0']))
    series = {}
    ii = 0
    timestamp = 0.0
    while f'S{ii}' in data.keys():
        series[timestamp] = data[f'S{ii}'].flatten()
        ii += 1
        timestamp += header['DeltaT']
    df = pd.DataFrame(data=series, index=frequencies)
    df.rename_axis('Frequency (Hz)', inplace=True)
    df.rename_axis('Time (s)', axis='columns', inplace=True)
    df = df.transpose()
    return (header, df)

def _get_xml_text(xml, path, default=None):
        el = xml.find(path)
        if el is not None:
            return el.text
        else:
            return default

def _create_header(data):
    it = ET.iterparse(StringIO(data['rsaMetadata'][0]))
    for _, el in it:
        if '}' in el.tag:
            el.tag = el.tag.split('}', 1)[1]  # strip all namespaces
    root = it.root

    header = {
        'Date': _get_xml_text(root,
            './DataSetsCollection/SpectrumDataSets/SpectrumDataDescription/DateTime', ''),
        'RBW': float(_get_xml_text(root, ".//*[@pid='rbw']/Value", 0)),
        'VBW': float(_get_xml_text(root, ".//*[@pid='vidBW']/Value", 0)),
        'Span': float(data['SpectraSpan']),
        'CenterFrequency': float(data['SpectraCenter']),
        'StartFrequency': float(data['SpectraCenter'] - data['SpectraSpan']/2),
        'StopFrequency': float(data['SpectraCenter'] + data['SpectraSpan']/2),
        'DeltaT': float(data['TDelta'][0][0])
    }
    return header
    
