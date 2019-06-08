import logging
import struct
import numpy as np

from .util import Structure, from_buffer

LOGGER = logging.getLogger(__name__)

BLOCK_IDS = {
        120: 'DSet2DC1DIBlock',
        121: 'HistoryRecordBlock',
        122: 'InstrHdrHistoryRecordBlock',
        123: 'InstrumentHeaderBlock',
        124: 'IRInstrumentHeaderBlock',
        125: 'UVInstrumentHeaderBlock',
        126: 'FLInstrumentHeaderBlock',
        -29839: 'DataSetDataTypeMember',
        -29838: 'DataSetAbscissaRangeMember',
        -29837: 'DataSetOrdinateRangeMember',
        -29836: 'DataSetIntervalMember',
        -29835: 'DataSetNumPointsMember',
        -29834: 'DataSetSamplingMethodMember',
        -29833: 'DataSetXAxisLabelMember',
        -29832: 'DataSetYAxisLabelMember',
        -29831: 'DataSetXAxisUnitTypeMember',
        -29830: 'DataSetYAxisUnitTypeMember',
        -29829: 'DataSetFileTypeMember',
        -29828: 'DataSetDataMember',
        -29827: 'DataSetNameMember',
        -29826: 'DataSetChecksumMember',
        -29825: 'DataSetHistoryRecordMember',
        -29824: 'DataSetInvalidRegionMember',
        -29823: 'DataSetAliasMember',
        -29822: 'DataSetVXIRAccyHdrMember',
        -29821: 'DataSetVXIRQualHdrMember',
        -29820: 'DataSetEventMarkersMember',
    }


def load_sp(filename, byte_order='<'):
    """
    Load a Perkin Elmer spectrum.

    Parameters
    ----------
    filename : str
        path to the Perkin Elmer spectrum file
    byte_order : str
        byte order of the encoded binary data

    Returns
    -------
    sp :
        Perkin Elmer spectrum data

    References
    ----------
    .. [1] Ben Perston. "PerkinElmer IR data file import tools",
       https://uk.mathworks.com/matlabcentral/fileexchange/22736-perkinelmer-ir-data-file-import-tools
    """
    data = Structure()

    with open(filename, 'rb') as fp:
        signature = fp.read(4)
        assert signature == b'PEPE'

        data['description'] = fp.read(40)

        while True:
            # Check whether the file is empty
            block_id = fp.read(2)
            if not block_id:
                break
            # Get the block identifier and block size
            block_id, = struct.unpack('h', block_id)
            block_id = BLOCK_IDS[block_id]
            block_size, = struct.unpack('i', fp.read(4))

            if block_id =='DSet2DC1DIBlock':
                # Wrapper block
                pass
            elif block_id == 'DataSetAbscissaRangeMember':
                _, data['start'], data['end'] = from_buffer('hdd', fp, byte_order)
            elif block_id == 'DataSetIntervalMember':
                _, data['delta'] = from_buffer('hd', fp, byte_order)
            elif block_id == 'DataSetNumPointsMember':
                _, data['num_points'] = from_buffer('hi', fp, byte_order)
            elif block_id == 'DataSetXAxisLabelMember':
                _, length = from_buffer('hh', fp, byte_order)
                data['xlabel'] = fp.read(length).decode()
            elif block_id == 'DataSetYAxisLabelMember':
                _, length = from_buffer('hh', fp, byte_order)
                data['ylabel'] = fp.read(length).decode()
            elif block_id == 'DataSetDataMember':
                _, length = from_buffer('hi', fp, byte_order)
                assert length == data['num_points'] * 8
                data['values'] = np.frombuffer(fp.read(length), '<d')
            elif block_id in [
                'DataSetHistoryRecordMember',
                'DataSetChecksumMember',
                'DataSetDataTypeMember',
                'DataSetNameMember',
                'DataSetOrdinateRangeMember',
                'DataSetXAxisUnitTypeMember',
                'DataSetYAxisUnitTypeMember',
                'DataSetSamplingMethodMember',
                'DataSetFileTypeMember',
                'DataSetAliasMember',
            ]:
                data[block_id] = fp.read(block_size)
                LOGGER.info(f'read block of type {block_id} without parsing')
            else:
                raise ValueError((block_id, fp.read(block_size)))

    data['wavelengths'] = data['start'] + data['delta'] * np.arange(data['num_points'])
    return data
