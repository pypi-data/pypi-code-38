import pytest


def test_unit_header(rubrik):
    header = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    assert rubrik._header() == header
