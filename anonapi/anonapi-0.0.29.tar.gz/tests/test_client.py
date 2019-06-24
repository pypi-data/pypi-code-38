#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for the `anonapi.client` module."""

import pytest

from anonapi.client import (
    WebAPIClient,
    APIClientAPIException,
    APIClientAuthorizationFailedException,
    APIClientException,
)
from tests.factories import RequestsMock, RequestsMockResponseExamples


def test_basic_client(mocked_requests_client: WebAPIClient):
    """Request documentation from server"""
    client, requests_mock = mocked_requests_client
    requests_mock: RequestsMock
    requests_mock.set_response(
        text=RequestsMockResponseExamples.API_CALL_NOT_DEFINED, status_code=404
    )
    assert "some docs" in str(client.get_documentation())


def test_get_jobs(mocked_requests_client: WebAPIClient):
    """Get info on last jobs from server"""
    client, requests_mock = mocked_requests_client

    # job list with two jobs.
    requests_mock.set_response(text=RequestsMockResponseExamples.JOBS_LIST_GET_JOBS)
    response = client.get("get_jobs")
    assert len(response) == 2


def test_get_job(mocked_requests_client: WebAPIClient):
    """Get info on a single job """
    client, requests_mock = mocked_requests_client

    # job info for a job with id=3
    requests_mock.set_response(text=RequestsMockResponseExamples.JOB_INFO)
    response = client.get("get_job", job_id=3)
    assert response["job_id"] == 3
    assert response["user_name"] == "z123sandbox"


def test_modify_job(mocked_requests_client: WebAPIClient):
    """Get info on a single job """
    client, requests_mock = mocked_requests_client

    # modify status. For a real server this would return the modified job. For test just return test job
    requests_mock.set_response(text=RequestsMockResponseExamples.JOB_INFO)
    _ = client.post("modify_job", job_id=3, status="INACTIVE")
    assert requests_mock.requests.post.called


def test_404_responses(mocked_requests_client: WebAPIClient):
    """If the API is running but there is an error, 400 is returned, but if other things are wrong (e.g. the whole api
    is not running, the url on server you are calling is not recognized) a 404 is returned. Handle these properly
    """
    client, requests_mock = mocked_requests_client
    requests_mock: RequestsMock

    # Calling an API method that is not recognized will yield a 404 with useful info. This should be no error
    requests_mock.set_response(
        text=RequestsMockResponseExamples.API_CALL_NOT_DEFINED, status_code=404
    )
    response = client.get("unknown_function")
    assert "404" in response.keys()
    assert "documentation" in response["404"]

    # Calling an activate server that is not an API
    requests_mock.set_response(
        text="welcome to totally_unrelated.com, your one-stop shop to oblivion",
        status_code=404,
    )
    with pytest.raises(APIClientException) as exception:
        client.get("get_job")
    assert "Is this a web API url?" in str(exception.value)


def test_server_not_found(mocked_requests_client: WebAPIClient):
    """Calling a url that does not exist should yield an APIClientException
    """
    client, requests_mock = mocked_requests_client
    requests_mock: RequestsMock

    requests_mock.set_response_exception(ConnectionError)
    with pytest.raises(APIClientException):
        _ = client.get("anything")

    with pytest.raises(APIClientException):
        _ = client.post("anything")


def test_wrong_inputs(mocked_requests_client: WebAPIClient):
    """Make some impossible requests of the server"""
    client, requests_mock = mocked_requests_client
    requests_mock: RequestsMock

    # getting non-existent job, Server will respond with
    requests_mock.set_response(
        text=RequestsMockResponseExamples.JOB_DOES_NOT_EXIST, status_code=400
    )
    with pytest.raises(APIClientAPIException) as exception:
        client.get("get_job", job_id=100)
    assert "does not exist" in str(exception.value)

    # passing insufficient parameters
    requests_mock.set_response(
        text=RequestsMockResponseExamples.REQUIRED_PARAMETER_NOT_SUPPLIED,
        status_code=400,
    )
    with pytest.raises(APIClientAPIException) as exception:
        client.get("get_job")
    assert "Required parameter" in str(exception.value)

    # passing insufficient parameters
    requests_mock.set_response(
        text=RequestsMockResponseExamples.API_CALL_NOT_DEFINED, status_code=400
    )
    with pytest.raises(APIClientAPIException) as exception:
        client.get("sgetdf_jfob")
    assert "The API call you tried to make is not defined" in str(exception.value)


def test_response_code_handling(mocked_requests_client: WebAPIClient):
    """Make some impossible requests of the server"""
    client, requests_mock = mocked_requests_client
    requests_mock: RequestsMock

    requests_mock.set_response(text="405 response!", status_code=405)
    with pytest.raises(APIClientException) as exception:
        client.get("get_jobs")
    assert "Method not allowed" in str(exception.value)

    requests_mock.set_response(
        text="you found these credentials in some garbage dump or sometin?",
        status_code=401,
    )
    with pytest.raises(APIClientAuthorizationFailedException) as exception:
        client.get("get_jobs")
    assert "Your credentials do not seem to work" in str(exception.value)

    # Superweird unexpected response from server should still raise correct exception
    requests_mock.set_response(text="Abandon all hope, ye who receive", status_code=666)
    with pytest.raises(APIClientException) as exception:
        client.get("get_jobs")
    assert "Unexpected response" in str(exception.value)
