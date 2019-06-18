"""Verifies the 'snomedct.py' module"""

from urllib.parse import urlparse

from nose.tools import ok_, raises

from petl import Record

from termlink.snomedct import Service, _to_json


def test_service_uri_can_be_file():
    """Checks that a uri.scheme of 'file' is ok"""
    uri = urlparse("file://")
    ok_(Service(uri=uri))


@raises(ValueError)
def test_service_uri_requires_scheme_file():
    """Checks that a uri.scheme of 'foobar' throws a ValueError"""
    uri = urlparse("foobar://")
    Service(uri=uri)


def test_to_json():
    """Checks that a record is properly converted to .json"""

    fields = ['effectiveTime', 'sourceId', 'destinationId', 'source.term', 'target.term', 'versioned']
    values = ('20160131', '425630003', '400195000', 'Acute irritant contact dermatitis (disorder)',
              'Contact hypersensitivity reaction (disorder)', False)
    record = Record(values, fields)
    actual = _to_json(record)

    ok_(actual[0])
