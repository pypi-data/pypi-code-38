import pytest
from requests.exceptions import HTTPError

from django.shortcuts import Http404

from directory_cms_client import helpers
from tests.helpers import create_response


@pytest.mark.parametrize('status_code,exception', (
    (400, HTTPError),
    (404, Http404),
    (500, HTTPError),
))
def test_handle_cms_response_error(status_code, exception):
    response = create_response(status_code=status_code)
    with pytest.raises(exception):
        helpers.handle_cms_response(response)


def test_handle_cms_response_ok():
    response = create_response(status_code=200, json_body={'1': '2'})
    assert helpers.handle_cms_response(response) == {'1': '2'}


@pytest.mark.parametrize('response,expected', (
    (create_response(status_code=200, json_body={'1': '2'}), {'1': '2'}),
    (create_response(status_code=404), {})
))
def test_handle_cms_response_okish(response, expected):
    assert helpers.handle_cms_response_allow_404(response) == expected
