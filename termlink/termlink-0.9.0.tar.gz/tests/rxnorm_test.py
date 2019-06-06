"""Verifies the 'rxnorm.py' module"""

from urllib.parse import urlparse

from nose.tools import ok_, raises, eq_

from petl import Record

from termlink.models import Coding, Relationship
from termlink.rxnorm import Service, _to_json, _to_system, _to_relationship


def test_service_uri_can_be_file():
    """Checks that a uri.scheme of 'file' is ok"""
    uri = urlparse("file://")
    ok_(Service(uri=uri))


@raises(ValueError)
def test_service_uri_requires_scheme_file():
    """Checks that a uri.scheme of 'foobar' throws a ValueError"""
    uri = urlparse("foobar://")
    Service(uri=uri)


def test_to_relationship():
    """Checks that a record is properly converted to a Relationship"""
    fields = ['REL', 'source.CODE', 'source.STR', 'source.SAB',
              'target.CODE', 'target.STR', 'target.SAB']
    values = (
        'RB',
        '313782',
        'Acetaminophen 325 MG Oral Tablet',
        'RXNORM',
        '1152843',
        'Acetaminophen Pill',
        'RXNORM'
    )

    rec = Record(values, fields)
    res = _to_relationship(rec)
    exp = Relationship(
        equivalence='subsumes',
        source=Coding(
            system='http://www.nlm.nih.gov/research/umls/rxnorm',
            code='313782',
            display='Acetaminophen 325 MG Oral Tablet'
        ),
        target=Coding(
            system='http://www.nlm.nih.gov/research/umls/rxnorm',
            code='1152843',
            display='Acetaminophen Pill'
        )
    )

    eq_(exp, res)


def test_to_json():
    """Checks that a record is properly converted to .json"""

    fields = ['REL', 'source.CODE', 'source.STR', 'source.SAB',
              'target.CODE', 'target.STR', 'target.SAB']
    values = (
        'RB',
        '313782',
        'Acetaminophen 325 MG Oral Tablet',
        'RXNORM',
        '1152843',
        'Acetaminophen Pill',
        'RXNORM'
    )

    src = Record(values, fields)
    res = _to_json(src)
    ok_(res)


def test_to_system():
    """Checks that an sab is correctly converted into a system"""
    sab = 'rxnorm'
    res = _to_system(sab)
    exp = 'http://www.nlm.nih.gov/research/umls/rxnorm'
    eq_(exp, res)
