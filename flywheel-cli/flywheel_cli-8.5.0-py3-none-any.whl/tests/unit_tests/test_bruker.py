import os
from flywheel_cli.bruker import parse_bruker_params
from flywheel_cli.importers.bruker_scan import format_timestamp_fn

TEST_DATA_PATH = os.path.join(os.path.dirname(__file__), 'test_data/bruker')

def test_bruker_subject_v5():
    path = os.path.join(TEST_DATA_PATH, 'subject.txt')
    with open(path, 'r') as f:
        results = parse_bruker_params(f)

    assert results
    assert results['SUBJECT_id'] == '010005-m00'
    assert results['SUBJECT_weight'] == '65'
    assert results['SUBJECT_name'] == '(<>, <010005-m00>)'
    assert results['SUBJECT_study_name'] == 'protocol 76'

def test_bruker_acq_v5():
    path = os.path.join(TEST_DATA_PATH, 'acqp.txt')
    with open(path, 'r') as f:
        results = parse_bruker_params(f)

    assert results
    assert results['ACQ_experiment_mode'] == 'SingleExperiment'
    assert results['ACQ_protocol_name'] == 'EPI_FID_200_fmri'
    assert results['ACQ_slice_offset'] == (
        '-49.000 -44.000 -39.000 -34.000 -29.000 -24.000 -19.000 -14.000 -9.000 -4.000 '
        '1.000 6.000 11.000 16.000 21.000 26.000 31.000 36.000 41.000 46.000 51.000'
    )
    assert results['ACQ_institution'] == 'Cambridge U.'


def test_format_timestamp():
    format_fn = format_timestamp_fn('test.key')
    key, value = format_fn('978611751')
    assert key == 'test.key'
    assert value == '2001-01-04T12:35:51Z'

    key, value = format_fn('1495041027')
    assert key == 'test.key'
    assert value == '2017-05-17T17:10:27Z'

    assert None == format_fn('foobar')

