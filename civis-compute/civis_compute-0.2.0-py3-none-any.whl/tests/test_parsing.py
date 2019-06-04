from __future__ import print_function
from __future__ import division

from six import StringIO

import pytest

from ..parsing import (
    _parse_options_from_file,
    _join_container_params,
    _cleanup_required_resources,
    _reformat_files_key,
    _process_options)


@pytest.mark.parametrize(
    'line',
    ["#CIVIS name=",
     "#CIVIS name",
     "#CIVIS name # bad",
     "#CIVIS name= # really?"])
def test_parse_options_from_file_raises_error(line):
    fp = StringIO(line)
    with pytest.raises(ValueError):
        _parse_options_from_file(fp)


def test_parse_options_from_file():
    fp = StringIO("""\
#CIVIS name= my file name
#CIVIS pip = [numpy, scipy]
#CIVIS d={'cpu': 1024, 'memory': 8192}
#CIVIS namec= my file name # ugh
#CIVIS pipc = [numpy, scipy] # double ugh
#CIVIS dc={'cpu': 1024, 'memory': 8192} # comments might break me
""")
    params = _parse_options_from_file(fp)

    test_params = {
        'name': 'my file name',
        'pip': ['numpy', 'scipy'],
        'd': {'cpu': 1024, 'memory': 8192},
        'namec': 'my file name',
        'pipc': ['numpy', 'scipy'],
        'dc': {'cpu': 1024, 'memory': 8192}}
    assert params == test_params, "Parsed parameters are not correct!"


@pytest.mark.parametrize(
    'req',
    [{'cpu': '1024', 'memory': 2048.0, 'disk_space': 10},
     {'cpu': '1024', 'memory': 2048.0, 'diskSpace': 10}])
def test_cleanup_required_resources(req):
    expected_req = {'cpu': 1024, 'memory': 2048, 'disk_space': 10.0}
    test_req = _cleanup_required_resources(req)
    assert test_req == expected_req, (
        "Required resources were not cleaned up "
        "properly.")
    assert isinstance(test_req['cpu'], int), "CPU is not an int!"
    assert isinstance(test_req['memory'], int), "Memory is not an int!"
    assert isinstance(test_req['disk_space'], float), (
        "Disk space is not a float!")


@pytest.mark.parametrize(
    'old,new,res', [
        ({}, {'a': 5}, {'a': 5}),
        ({'a': 5}, {}, {'a': 5}),
        ({'a': 5}, {'a': 6}, {'a': 6}),
        ({'required_resources': {'a': 5}},
         {'required_resources': {'a': 6}},
         {'required_resources': {'a': 6}}),
        ({'required_resources': {'a': 5}},
         {},
         {'required_resources': {'a': 5}}),
        ({},
         {'required_resources': {'a': 6}},
         {'required_resources': {'a': 6}}),
        ({'arguments': {'a': 5}},
         {'arguments': {'a': 6}},
         {'arguments': {'a': 6}}),
        ({'arguments': {'a': 5}},
         {},
         {'arguments': {'a': 5}}),
        ({},
         {'arguments': {'a': 6}},
         {'arguments': {'a': 6}}),
        ({'params': [{'name': 'a', 'value': 10}]},
         {'params': [{'name': 'a', 'value': 11}]},
         {'params': [{'name': 'a', 'value': 11}]}),
        ({'params': [{'name': 'a', 'value': 10}, {'name': 'b', 'value': 11}]},
         {'params': [{'name': 'a', 'value': 11}]},
         {'params': [{'name': 'a', 'value': 11}, {'name': 'b', 'value': 11}]}),
        ({'params': [{'name': 'a', 'value': 10}]},
         {'params': [{'name': 'a', 'value': 11}, {'name': 'b', 'value': 11}]},
         {'params': [{'name': 'a', 'value': 11}, {'name': 'b', 'value': 11}]}),
        ({},
         {'params': [{'name': 'a', 'value': 11}]},
         {'params': [{'name': 'a', 'value': 11}]}),
        ({'params': [{'name': 'a', 'value': 10}]},
         {},
         {'params': [{'name': 'a', 'value': 10}]}),
        ({'files': ['a']}, {'files': ['b']}, {'files': ['a', 'b']}),
        ({}, {'files': ['b']}, {'files': ['b']}),
        ({'files': ['a']}, {}, {'files': ['a']})])
def test_join_container_params(old, new, res):
    _join_container_params(old, new)
    assert set(old) == set(res), "Parameters were not updated properly!"


@pytest.mark.parametrize(
    'params,res', [
        ({'files': ['a']}, {'files': ['a']}),
        ({}, {}),
        ({'files': 'a'}, {'files': ['a']}),
        ({'files': '   ,a,\n   '}, {'files': ['a']}),
        ({'files': '   ,a,\n   ,b,,  ,\n ,,'}, {'files': ['a', 'b']}),
        ({'files': '   a\n   '}, {'files': ['a']})])
def test_reformat_files_key(params, res):
    _reformat_files_key(params)
    assert params == res, "The 'files' key was not reformatted properly!"


@pytest.mark.parametrize('script_type', ['r', 'python'])
def test_process_options(client, script_type):
    params = {
        'a': 2, 'b': 3, 'required_resources': {'cpu': 8192.0},
        'files': 'a,   ,\n,,b'}
    cli_params = {
        'b': None, 'a': 4, 'c': 6, 'required_resources': {'memory': 10.0},
        'files': 'c,d'}

    test_params = _process_options(params, script_type, cli_params, client)

    expected_params = {
        'required_resources': {'cpu': 8192, 'memory': 10, 'disk_space': 16.0},
        'a': 4,
        'b': 3,
        'c': 6,
        'use_file_cache': False,
        'files': ['a', 'b', 'c', 'd']}

    if script_type == 'r':
        expected_params['docker_image_name'] = 'civisanalytics/datascience-r'
    else:
        expected_params['docker_image_name'] \
            = 'civisanalytics/datascience-python'
        expected_params['repo_cmd'] = 'python setup.py install'

    assert test_params == expected_params


@pytest.mark.parametrize('aws_cred_id', [None, 5])
def test_process_options_add_aws_creds(client, aws_cred_id):
    params = {
        'a': 2,
        'b': 3,
        'docker_image_name': 'p',
        'add_aws_creds': True,
        'aws_cred_id': aws_cred_id,
        'params': [{'name': 't', 'value': 5}]}
    cli_params = {'b': None, 'a': 4, 'c': 6}

    test_params = _process_options(params, 'r', cli_params, client)
    assert test_params == {
        'required_resources': {
            'cpu': 1024, 'memory': 8192, 'disk_space': 16.0},
        'a': 4,
        'b': 3,
        'c': 6,
        'docker_image_name': 'p',
        'use_file_cache': False,
        'arguments': {'AWS': aws_cred_id or 0},
        'params': [
            {'name': 't', 'value': 5},
            {'name': 'AWS', 'type': 'credential_aws'}]
        }, "Processed parameters are not right!"
