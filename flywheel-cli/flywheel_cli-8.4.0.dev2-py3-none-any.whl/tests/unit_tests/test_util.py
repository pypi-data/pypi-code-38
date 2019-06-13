from flywheel_cli.util import is_dicom_file


def test_is_dicom_file():
    assert is_dicom_file('test.dcm')
    assert is_dicom_file('test.DCM')
    assert is_dicom_file('test.dicom')
    assert is_dicom_file('test.DICOM')
    assert is_dicom_file('test.dcm.gz')
    assert is_dicom_file('test.DCM.GZ')
    assert is_dicom_file('test.dicom.gz')
    assert is_dicom_file('test.DICOM.GZ')
    assert is_dicom_file('/full/path/to/test.dcm')

    assert not is_dicom_file('')
    assert not is_dicom_file('/')
    assert not is_dicom_file('/test.txt')
    assert not is_dicom_file('/dcm.test')
    assert not is_dicom_file('test.dcmisnt')
    assert not is_dicom_file('test.dcm.zip')
