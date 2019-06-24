#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for the `anonapi.anon` module."""
from typing import Tuple
from unittest.mock import Mock

import pytest
from pytest import fixture

from anonapi.cli import (
    AnonCommandLineParser,
    AnonClientTool,
    AnonCommandLineParserException,
    ClientToolException)
from anonapi.batch import BatchFolder, JobBatch
from anonapi.objects import RemoteAnonServer
from anonapi.settings import DefaultAnonClientSettings
from tests.factories import RequestsMock, RequestsMockResponseExamples


class NonPrintingAnonCommandLineParser(AnonCommandLineParser):
    """For test purposes. Just to indicate that this class has a mock_console attribute"""

    mock_console = None


class MockConsole:
    """A console with a print function that just records

    """

    def __init__(self):
        self.content = []

    def print(self, msg):
        self.content.append(msg)

    def all_content(self):
        return "\n".join(self.content)

    def last_print(self):
        return self.content[-1]

    def assert_called(self):
        assert self.content


@fixture
def non_printing_test_parser():
    """A command line tool instance with a Mock() client tool, so no actual calls are made.
    Also, printing to console instead logged to mock_console

    Returns
    -------
    AnonCommandLineParser with additional field 'mock_console' that records output

    """
    settings = DefaultAnonClientSettings()
    parser = NonPrintingAnonCommandLineParser(client_tool=Mock(), settings=settings)

    parser.mock_console = MockConsole()
    parser.print_to_console = parser.mock_console.print
    return parser


@fixture
def test_parser_and_mock_requests(mocked_requests_client):
    """A console client instance that does not call real servers, but calls a mock requests lib (RequestsMock)
     instead. the RequestMock responses can be set to arbitrary values

    Parameters
    ----------
    mocked_requests_client: conftest.mocked_requests_client pytest fixture

    Returns
    -------
    AnonCommandLineParser, RequestsMock:
        A console client instance that does not call real servers, but calls a mock requests lib (RequestsMock)
        instead. the RequestMock responses can be set to arbitrary values

    """

    client, requests_mock = mocked_requests_client
    client_tool = AnonClientTool(username="testuser", token="test_token")

    def mock_get_client(url):
        client.hostname = url
        return client

    client_tool.get_client = mock_get_client
    parser = AnonCommandLineParser(
        client_tool=client_tool, settings=DefaultAnonClientSettings()
    )
    return parser, requests_mock


@fixture
def test_parser_and_mock_requests_non_printing(
    mocked_requests_client, non_printing_test_parser
):
    """Same as test_parser_and_mock_requests, but the returned parser has a .mock_console attribute that records all
    printing to console

    Parameters
    ----------
    mocked_requests_client: conftest.mocked_requests_client pytest fixture

    Returns
    -------
    AnonCommandLineParser, RequestsMock:
        A console client instance that does not call real servers, but calls a mock requests lib (RequestsMock)
        instead. the RequestMock responses can be set to arbitrary values

    """

    client, requests_mock = mocked_requests_client
    client_tool = AnonClientTool(username="testuser", token="test_token")

    def mock_get_client(url):
        client.hostname = url
        return client

    client_tool.get_client = mock_get_client

    parser = non_printing_test_parser
    parser.client_tool = client_tool

    return parser, requests_mock


@fixture
def extended_test_parser_and_mock_requests(test_parser_and_mock_requests):
    """Identical to test_parser_and_mock_requests(), but the console client instance has 3 extra servers


    Parameters
    ----------
    test_parser_and_mock_requests: conftest.mocked_requests_client pytest fixture

    Returns
    -------
    (AnonCommandLineParser, RequestsMock):
        A console client instance that does not call real servers, but calls a mock requests lib (RequestsMock)
        instead. the RequestMock responses can be set to arbitrary values

    """
    parser, requests_mock = test_parser_and_mock_requests
    settings = parser.settings
    settings.servers.append(
        RemoteAnonServer(name="sandbox", url="https://umcradanonp11.umcn.nl/sandbox")
    )
    settings.servers.append(
        RemoteAnonServer(name="wrong", url="https://umcradanonp11.umcn.nl/non_existant")
    )
    settings.servers.append(
        RemoteAnonServer(name="p01", url="https://umcradanonp11.umcn.nl/p01")
    )

    return parser, requests_mock


def test_command_line_tool_basic(
    test_parser_and_mock_requests: Tuple[AnonCommandLineParser, RequestsMock], capsys
):
    """Test some commands"""
    parser, requests_mock = test_parser_and_mock_requests
    parser.execute_command("status".split(" "))

    captured = capsys.readouterr()
    assert "Available servers" in str(captured)


def test_command_line_tool_status_without_active_server(
    test_parser_and_mock_requests, capsys
):
    """Error found live, making sure its fixed """
    parser, requests_mock = test_parser_and_mock_requests
    parser.settings.active_server = None

    # this should not crash
    parser.get_status()

    assert "Available servers" in str(capsys.readouterr().out)


@pytest.mark.parametrize(
    "command, expected_server_list_length",
    [
        ("server list".split(" "), 1),  # you start with one server
        (
            "server add server2 https://something.com".split(" "),
            2,
        ),  # after adding a server you should have two
        ("server remove test".split(" "), 0),  # if you remove it there should be none
    ],
)
def test_command_line_tool_add_remove_server(
    test_parser_and_mock_requests, capsys, command, expected_server_list_length
):
    """Test commands to add, remove servers and see whether the number servers that are known is correct"""
    parser, _ = test_parser_and_mock_requests
    parser.execute_command(command)
    _ = capsys.readouterr()  # make sure there is no printing
    assert len(parser.settings.servers) == expected_server_list_length


def test_command_line_tool_server_status(test_parser_and_mock_requests, capsys):
    """Test checking status"""
    parser, requests_mock = test_parser_and_mock_requests
    requests_mock: RequestsMock

    # A server that is not in the list should generate a nice message, but not hit any server
    parser.execute_command("server status some_server".split(" "))
    assert "Unknown server" in capsys.readouterr().out
    assert not requests_mock.called()

    # 'test': a server that is in the list and responds. This should give you an OK message
    # API_CALL_NOT_DEFINED is a response that is used to check the liveness of a server currently.
    requests_mock.set_response(RequestsMockResponseExamples.API_CALL_NOT_DEFINED)
    parser.execute_command("server status test".split(" "))
    assert "OK" in capsys.readouterr().out

    # now test a non-responsive server:
    requests_mock.set_response_exception(ConnectionError)
    parser.execute_command("server status test".split(" "))
    assert "ERROR" in capsys.readouterr().out


def test_command_line_tool_job_info(extended_test_parser_and_mock_requests, capsys):
    """Test checking status"""
    parser, requests_mock = extended_test_parser_and_mock_requests
    requests_mock: RequestsMock

    parser.execute_command("server activate sandbox".split(" "))
    assert "Set active server to" in capsys.readouterr().out

    requests_mock.set_response(text=RequestsMockResponseExamples.JOB_INFO)
    parser.execute_command("job info 3".split(" "))
    output = capsys.readouterr().out
    assert "job 3 on sandbox" in output
    assert "'user_name', 'z123sandbox'" in output


def test_command_line_tool_activate_server(
    extended_test_parser_and_mock_requests, capsys
):
    """Test activating a server"""
    parser, _ = extended_test_parser_and_mock_requests

    parser.execute_command("server activate sandbox".split(" "))
    parser.get_active_server().name == "sandbox"

    # activate a non-existant server name should just give a nice message, no crashes
    parser.execute_command("server activate yomomma".split(" "))
    assert "Unknown server" in capsys.readouterr().out
    assert parser.get_active_server().name == "sandbox"


def test_command_line_tool_job_functions(
    extended_test_parser_and_mock_requests, capsys
):
    """Check a whole lot of commands without doing actual queries

    Kind of a mop up test trying to get coverage up"""
    parser, requests_mock = extended_test_parser_and_mock_requests
    requests_mock: RequestsMock

    requests_mock.set_response(text=RequestsMockResponseExamples.JOB_INFO)
    parser.execute_command("job info 1234".split(" "))
    assert requests_mock.requests.get.called is True
    assert "1234" in str(requests_mock.requests.get.call_args)

    requests_mock.reset()
    parser.execute_command("job reset 1234".split(" "))
    assert requests_mock.requests.post.called is True
    assert "'files_downloaded': 0" in str(requests_mock.requests.post.call_args)

    requests_mock.reset()
    parser.execute_command("job cancel 1234".split(" "))
    assert requests_mock.requests.post.called is True
    assert "cancel" in str(requests_mock.requests.post.call_args)

    # can't reset a job when there is no server
    capsys.readouterr()  # purge previous output
    parser.settings.active_server = None
    requests_mock.reset()
    parser.execute_command("job reset 1234".split(" "))
    assert requests_mock.requests.post.called is False
    assert "No active server. Which one do you want to use?" in capsys.readouterr().out


def test_command_line_tool_job_list(extended_test_parser_and_mock_requests, capsys):
    parser, requests_mock = extended_test_parser_and_mock_requests
    requests_mock: RequestsMock

    requests_mock.reset()
    with pytest.raises(ClientToolException):
        parser.execute_command("job list 1 2 3 445".split(" "))


@pytest.mark.parametrize(
    "command, server_response, expected_print",
    [
        (
            "server jobs".split(" "),
            RequestsMockResponseExamples.JOBS_LIST_GET_JOBS,
            "most recent 50 jobs on test:",
        ),
        (
            "server jobs no-server".split(" "),
            "",
            "Unknown server",
        ),  # server no-server does not exist. No calls to client expected
        (
            "server status test".split(" "),
            RequestsMockResponseExamples.API_CALL_NOT_DEFINED,
            "OK",
        ),  # server test exists, should work
        (
            "status".split(" "),
            "",
            "Available servers",
        ),  # general status should not hit server
    ],
)
def test_command_line_tool_server_functions(
    extended_test_parser_and_mock_requests,
    capsys,
    command,
    server_response,
    expected_print,
):
    """Check a whole lot of commands without doing actual queries

    Kind of a mop up test trying to get coverage up"""

    parser, requests_mock = extended_test_parser_and_mock_requests
    requests_mock: RequestsMock

    requests_mock.set_response(text=server_response)
    parser.execute_command(command)
    assert expected_print in capsys.readouterr().out


def test_get_server_when_none_is_active(extended_test_parser_and_mock_requests, capsys):
    """In certain cases active server can be None. handle this gracefully

    """
    parser, _ = extended_test_parser_and_mock_requests
    capsys.readouterr()  # stop any printing to console
    parser.settings.active_server = None
    # Calling for server here should fail because there is no active server
    with pytest.raises(AnonCommandLineParserException):
        parser.get_active_server()


def test_command_line_tool_user_functions(
    extended_test_parser_and_mock_requests, capsys
):
    parser, _ = extended_test_parser_and_mock_requests
    parser: AnonCommandLineParser
    assert parser.settings.user_name != "test_changed"

    parser.execute_command("user set_username test_changed".split(" "))
    assert parser.settings.user_name == "test_changed"

    parser.execute_command("user info".split(" "))
    assert "user" in capsys.readouterr().out

    token_before = parser.settings.user_token
    parser.execute_command("user get_token".split(" "))
    assert "Got and saved api token" in capsys.readouterr().out
    token_after = parser.settings.user_token
    assert token_before != token_after  # token should have changed


@pytest.mark.parametrize(
    "command, expected_output",
    [
        ("server jobs", "Error getting jobs"),
        ("job info 123", "Error getting job info"),
        ("server status", "is not responding properly"),
        ("job cancel 123", "Error cancelling job"),
        ("job reset 123", "Error resetting job"),
        ("server status", "is not responding properly"),
    ],
)
def test_client_tool_exception_response(
    test_parser_and_mock_requests, capsys, command, expected_output
):
    """The client that the command line tool is using might yield exceptions. Handle gracefully

    """
    parser, requests_mock = test_parser_and_mock_requests

    # any call to server will yield error
    requests_mock.set_response_exception(ConnectionError)

    parser.execute_command(command.split(" "))
    assert expected_output in capsys.readouterr().out


def test_cli_batch(test_parser_and_mock_requests_non_printing, tmpdir):
    """Try working with a batch of job ids from console"""
    parser, _ = test_parser_and_mock_requests_non_printing
    parser.current_dir = lambda: str(
        tmpdir
    )  # make parser thinks tmpdir is its working dir

    parser.execute_command("batch info".split(" "))
    assert "Error: No batch defined" in parser.mock_console.content[0]

    assert not BatchFolder(tmpdir).has_batch()
    parser.execute_command("batch init".split(" "))
    assert BatchFolder(tmpdir).has_batch()

    parser.execute_command("batch add 1 2 3 345".split(" "))
    assert BatchFolder(tmpdir).load().job_ids == ["1", "2", "3", "345"]

    parser.execute_command(
        "batch add 1 2 50".split(" ")
    )  # duplicates should be silently ignored
    assert BatchFolder(tmpdir).load().job_ids == ["1", "2", "3", "345", "50"]

    parser.execute_command(
        "batch remove 50 345 1000".split(" ")
    )  # non-existing keys should be ignored
    assert BatchFolder(tmpdir).load().job_ids == ["1", "2", "3"]

    parser.execute_command("batch remove 1 2 3".split(" "))
    assert BatchFolder(tmpdir).load().job_ids == []

    parser.execute_command("batch delete".split(" "))
    assert not BatchFolder(tmpdir).has_batch()


def test_cli_batch_status(test_parser_and_mock_requests_non_printing):
    """Try operations actually calling server"""

    parser, requests_mock = test_parser_and_mock_requests_non_printing
    batch = JobBatch(
        job_ids=["1000", "1002", "5000"], server=parser.get_server_or_active_server()
    )
    parser.get_batch = lambda: batch  # set current batch to mock batch

    requests_mock.set_response(
        text=RequestsMockResponseExamples.JOBS_LIST_GET_JOBS_LIST
    )
    parser.batch_status()
    assert all(
        text in parser.mock_console.content[1]
        for text in ["DONE", "UPLOAD", "1000", "1002", "5000"]
    )


def test_cli_batch_status_errors(test_parser_and_mock_requests_non_printing):
    """Call server, but not all jobs exist. This should appear in the status message to the user"""

    parser, requests_mock = test_parser_and_mock_requests_non_printing
    batch = JobBatch(
        job_ids=["1000", "1002", "5000", "100000"],
        server=parser.get_server_or_active_server(),
    )
    parser.get_batch = lambda: batch  # set current batch to mock batch

    requests_mock.set_response(
        text=RequestsMockResponseExamples.JOBS_LIST_GET_JOBS_LIST
    )
    parser.batch_status()
    assert "NOT_FOUND    1" in parser.mock_console.content[3]


def test_cli_batch_status(test_parser_and_mock_requests_non_printing):
    """Try operations actually calling server"""

    parser, requests_mock = test_parser_and_mock_requests_non_printing
    batch = JobBatch(
        job_ids=["1000", "1002", "5000"], server=parser.get_server_or_active_server()
    )
    parser.get_batch = lambda: batch  # set current batch to mock batch
    parser.confirm = lambda x: True  # always answer yes on any user question
    parser.batch_reset()

    assert requests_mock.requests.post.call_count == 3  # Reset request should have been sent for each job id

    requests_mock.requests.reset_mock()
    parser.confirm = lambda x: False  # now answer no when asked are you sure
    parser.batch_reset()
    assert requests_mock.requests.post.call_count == 0  # No requests should have been sent


def test_cli_batch_reset_error(test_parser_and_mock_requests_non_printing):
    """Try operations actually calling server"""

    parser, requests_mock = test_parser_and_mock_requests_non_printing
    batch = JobBatch(
        job_ids=["1000", "1002", "5000"], server=parser.get_server_or_active_server()
    )
    parser.get_batch = lambda: batch  # set current batch to mock batch

    requests_mock.set_response(
        text=RequestsMockResponseExamples.JOBS_LIST_GET_JOBS_LIST_WITH_ERROR
    )
    parser.confirm = lambda x: True  # always answer yes on any user question

    parser.batch_reset_errors()
    assert requests_mock.requests.post.call_count == 2
