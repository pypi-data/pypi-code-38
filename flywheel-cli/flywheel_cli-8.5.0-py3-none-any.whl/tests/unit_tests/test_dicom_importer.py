import copy
import pytest
import pydicom
from flywheel_migration import DicomFile

from flywheel_cli.importers import DicomScanner
from flywheel_cli.config import Config
from flywheel_cli.walker import PyFsWalker

from .test_container_factory import MockContainerResolver

class mock(object):
    def __init__(self, **kwargs):
        self.__dict__ = kwargs

    def get_manufacturer(self):
        return self.__dict__.get('Manufacturer')

    def get(self, value):
        return self.__dict__.get(value)


def mock_dcm(value):
    if isinstance(value, dict):
        return mock(**{key: mock_dcm(val) for key, val in value.items()}, return_value=None)
    elif isinstance(value, list):
        return [mock_dcm(val) for val in value]
    else:
        return value


def test_resolve_acquisition():
    config = Config()
    dicom_scanner = DicomScanner(config)
    dcm = mock_dcm({'raw': {'StudyInstanceUID': '1', 'SeriesInstanceUID': '1', 'StudyDate': '12341212121212', 'StudyDescription': 'Session', 'SeriesDescription': 'Acq', 'SeriesDate': '19700101'}})
    acquisition = dicom_scanner.resolve_acquisition({}, dcm)
    assert acquisition.context['acquisition']['label'] == 'Acq'


def test_resolve_acquisition_secondary():
    config = Config()
    config.related_acquisitions = True
    dicom_scanner = DicomScanner(config)
    secondary_dcm_dict = {
        'StudyInstanceUID': 'study-uid',
        'SeriesInstanceUID': 'series-uid-2',
        'StudyDate': '12341212121212',
        'StudyDescription': 'Session',
        'SeriesDescription': 'Acq',
        'SeriesDate': '19700101',
        'ReferencedFrameOfReferenceSequence': [{
            'RTReferencedStudySequence': [{
                'RTReferencedSeriesSequence': [{
                    'SeriesInstanceUID': 'series-uid-1'
                }]
            }]
        }]
    }
    secondary_dcm_dict['raw'] = copy.deepcopy(secondary_dcm_dict)
    secondary_dcm = mock_dcm(secondary_dcm_dict)
    acquisition = dicom_scanner.resolve_acquisition({}, secondary_dcm)

    assert dicom_scanner.sessions['study-uid'].secondary_acquisitions['series-uid-1'] == acquisition


def test_resolve_primary_after_secondary():
    config = Config()
    config.related_acquisitions = True
    dicom_scanner = DicomScanner(config)
    secondary_dcm_dict = {
        'StudyInstanceUID': 'study-uid',
        'SeriesInstanceUID': 'series-uid-2',
        'StudyDate': '12341212121212',
        'StudyDescription': 'Session',
        'SeriesDescription': 'Acq',
        'SeriesDate': '19700101',
        'SOPInstanceUID': '1',
        'ReferencedFrameOfReferenceSequence': [{
            'RTReferencedStudySequence': [{
                'RTReferencedSeriesSequence': [{
                    'SeriesInstanceUID': 'series-uid-1'
                }]
            }]
        }]
    }
    secondary_dcm_dict['raw'] = copy.deepcopy(secondary_dcm_dict)
    secondary_dcm = mock_dcm(secondary_dcm_dict)
    acquisition = dicom_scanner.resolve_acquisition({}, secondary_dcm)
    # Add the file to the acquisition
    acquisition.files['series-uid-2'] = {'1': 'filepath'}
    acquisition.filenames['series-uid-2'] = 'secondary-filename'

    primary_dcm_dict = {
        'StudyInstanceUID': 'study-uid',
        'SeriesInstanceUID': 'series-uid-1',
        'StudyDate': '12341212121212',
        'StudyDescription': 'Session',
        'SeriesDescription': 'Primary',
    }
    primary_dcm_dict['raw'] = copy.deepcopy(primary_dcm_dict)
    primary_dcm = mock_dcm(primary_dcm_dict)
    acquisition = dicom_scanner.resolve_acquisition({}, primary_dcm)

    assert not dicom_scanner.sessions['study-uid'].secondary_acquisitions.get('sereies-uid-1')
    assert dicom_scanner.sessions['study-uid'].acquisitions['series-uid-1'] == acquisition
    assert acquisition.files['series-uid-2']['1'] == 'filepath'
    assert acquisition.filenames['series-uid-2'] == 'secondary-filename'


def test_resolve_primary_before_secondary():
    config = Config()
    config.related_acquisitions = True
    dicom_scanner = DicomScanner(config)

    primary_dcm_dict = {
        'StudyInstanceUID': 'study-uid',
        'SeriesInstanceUID': 'series-uid-1',
        'StudyDate': '12341212121212',
        'StudyDescription': 'Session',
        'SeriesDescription': 'Primary',
    }
    primary_dcm_dict['raw'] = copy.deepcopy(primary_dcm_dict)
    primary_dcm = mock_dcm(primary_dcm_dict)
    acquisition = dicom_scanner.resolve_acquisition({}, primary_dcm)

    secondary_dcm_dict = {
        'StudyInstanceUID': 'study-uid',
        'SeriesInstanceUID': 'series-uid-2',
        'StudyDate': '12341212121212',
        'StudyDescription': 'Session',
        'SeriesDescription': 'Acq',
        'SeriesDate': '19700101',
        'SOPInstanceUID': '1',
        'ReferencedFrameOfReferenceSequence': [{
            'RTReferencedStudySequence': [{
                'RTReferencedSeriesSequence': [{
                    'SeriesInstanceUID': 'series-uid-1'
                }]
            }]
        }]
    }
    secondary_dcm_dict['raw'] = copy.deepcopy(secondary_dcm_dict)
    secondary_dcm = mock_dcm(secondary_dcm_dict)
    acquisition = dicom_scanner.resolve_acquisition({}, secondary_dcm)
    # Add the file to the acquisition
    acquisition.files['series-uid-2'] = {'1': 'filepath'}
    acquisition.filenames['series-uid-2'] = 'secondary-filename'

    assert not dicom_scanner.sessions['study-uid'].secondary_acquisitions.get('sereies-uid-1')
    assert dicom_scanner.sessions['study-uid'].acquisitions['series-uid-1'] == acquisition
    assert acquisition.files['series-uid-2']['1'] == 'filepath'
    assert acquisition.filenames['series-uid-2'] == 'secondary-filename'


def test_resolve_acquisition_malformed_secondary():
    config = Config()
    config.related_acquisitions = True
    dicom_scanner = DicomScanner(config)
    dcm_dict = {
        'StudyInstanceUID': '1',
        'SeriesInstanceUID': '1',
        'StudyDate': '12341212121212',
        'StudyDescription': 'Session',
        'SeriesDescription': 'Acq',
        'SeriesDate': '19700101',
        'ReferencedFrameOfReferenceSequence': [{
            'RTReferencedStudySequence': 3
        }]
    }
    dcm_dict['raw'] = copy.deepcopy(dcm_dict)
    dcm = mock_dcm(dcm_dict)
    acquisition = dicom_scanner.resolve_acquisition({}, dcm)

    assert dicom_scanner.sessions['1'].acquisitions['1'] == acquisition

