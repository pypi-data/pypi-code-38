"""Verifies the 'hpo.py' module"""

from urllib.parse import urlparse

from nose.tools import ok_, raises, eq_

from parameterized import parameterized

from pronto import Term

from termlink.hpo import Service, _to_equivalence_from_scope, _to_system, _to_coding, _to_relationship
from termlink.models import Coding, Relationship


def test_service_uri_can_be_file():
    """Checks that a uri.scheme of 'file' is ok"""
    uri = urlparse("file://")
    ok_(Service(uri=uri))


@raises(ValueError)
def test_service_uri_requires_scheme_file():
    """Checks that a uri.scheme of 'foobar' throws a ValueError"""
    uri = urlparse("foobar://")
    Service(uri=uri)


@parameterized([
    ('BROAD', 'wider'),
    ('NARROW', 'narrower'),
    ('EXACT', 'equivalent'),
    ('RELATED', 'relatedto')
])
def test_to_equivalence_from_scope(scope, exp):
    """Checks that each scope converts"""
    res = _to_equivalence_from_scope(scope)
    ok_(exp == res)


@raises(RuntimeError)
def test_to_equivalence_from_scope_throws_runtime_error():
    """Checks that a runtime error is thrown for invalid scope"""
    _to_equivalence_from_scope('foobar')


@parameterized([
    ('HP', 'http://www.human-phenotype-ontology.org/')
])
def test_to_system(abbreviation, exp):
    """Checks that each scope converts"""
    res = _to_system(abbreviation)
    ok_(exp == res)


@raises(RuntimeError)
def test_to_system_throws_runtime_error():
    """Checks that a runtime error is thrown for invalid abbrevation"""
    _to_system('foobar')


def test_to_coding():
    """Checks that a term is properly converted to a coding"""

    term = Term(id='HP:0000001', name='All')

    res = _to_coding(term)

    exp = Coding(
        system='http://www.human-phenotype-ontology.org/',
        code='0000001',
        display='All'
    )

    ok_(exp == res)


def test_to_relationship():
    """Checks that a source, equivalence and target and properly converted"""

    source = Term(id='HP:0000107', name='Renal cyst')
    equivalence = 'subsumes'
    target = Term(id='HP:0000003', name='Multicystic kidney dysplasia')

    res = _to_relationship(source, equivalence, target)

    exp = Relationship(
        equivalence='subsumes',
        source=Coding(
            system='http://www.human-phenotype-ontology.org/',
            code='0000107',
            display='Renal cyst'
        ),
        target=Coding(
            system='http://www.human-phenotype-ontology.org/',
            code='0000003',
            display='Multicystic kidney dysplasia'
        )
    )

    eq_(exp, res)
