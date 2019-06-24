import json

import pytest

from anonapi.responses import format_job_info_list, parse_job_infos_response, APIParseResponseException
from tests.factories import RequestsMockResponseExamples


def test_jobs_response():
    response_raw = (json.loads(RequestsMockResponseExamples.JOBS_LIST_GET_JOBS))
    info_list = parse_job_infos_response(response_raw)

    list_str = format_job_info_list(info_list)
    assert list_str  # Just check that something was returned and nothing crashed
    assert len(info_list) == 2

    response_raw = (json.loads(RequestsMockResponseExamples.JOBS_LIST_GET_JOBS_LIST))
    info_list = parse_job_infos_response(response_raw)
    assert [x.status for x in info_list] == ['DONE', 'UPLOADED', 'UPLOADED']

    list_str = format_job_info_list(info_list)
    assert list_str


def test_jobs_response_exception():

    with pytest.raises(APIParseResponseException):
        parse_job_infos_response('definitly a wrong response')

    with pytest.raises(APIParseResponseException):
        parse_job_infos_response({'1': {'message': 'also not great'}})
