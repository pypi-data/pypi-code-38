import pytest
import pygass as pya
from pygass import constants as st


def valid_state(response):
    return response["hitParsingResult"][-1]["valid"]


def valid_url(response):
    return response["hitParsingResult"][-1]["hit"]


def valid_message(response):
    return response["parserMessage"][-1]["description"]


def assert_result(result, url):
    assert valid_state(result) is True
    assert valid_message(result) == "Found 1 hit in the request."
    assert valid_url(result).lower() == url.lower()
