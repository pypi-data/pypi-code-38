"""Verifies the 'common.py' module"""

from argparse import Namespace

import pkg_resources

from nose.tools import eq_, ok_, raises

from pronto import Term

from termlink.common import _to_coding, _to_relationship, execute
from termlink.models import Coding, Relationship


@raises(ValueError)
def test_uri_scheme():
    """An unsupported URI scheme throws a ValueError"""
    execute(Namespace(uri='foo://bar'))


def test_obo_format():
    """Tests the conversion of an .obo file"""
    path = pkg_resources.resource_filename(__name__, "resources/ontology.obo")
    uri = f"file://{path}"
    system = 'https://lifeomic.github.io/termlink/'
    output = execute(Namespace(uri=uri, system=system))
    ok_(len(output) > 0)


def test_owl_format():
    """Tests the conversion of an .owl file"""
    path = pkg_resources.resource_filename(__name__, "resources/ontology.owl")
    uri = f"file://{path}"
    system = 'https://lifeomic.github.io/termlink/'
    output = execute(Namespace(uri=uri, system=system))
    ok_(len(output) > 0)


def test_to_coding():
    """Checks that a term is properly converted"""

    system = "http://snomed.info/sct"
    term = Term(id='SNOMEDCT_US:25064002', name='Headache')

    res = _to_coding(term, system)

    exp = Coding(
        system=system,
        code='25064002',
        display='Headache'
    )

    eq_(exp, res)


def test_to_coding_without_colon():
    """Checks that a term without a ':' is properly converted"""

    system = "http://snomed.info/sct"
    term = Term(id='25064002', name='Headache')

    res = _to_coding(term, system)

    exp = Coding(
        system=system,
        code='25064002',
        display='Headache'
    )

    eq_(exp, res)


def test_to_json():
    """Checks that a source, equivalence and target and properly converted"""

    system = "http://snomed.info/sct"
    source = Term(id='SNOMEDCT_US:735938006', name='Acute headache')
    equivalence = 'subsumes'
    target = Term(id='SNOMEDCT_US:25064002', name='Headache')

    res = _to_relationship(source, equivalence, target, system)

    exp = Relationship(
        equivalence='subsumes',
        source=Coding(
            system=system,
            code='735938006',
            display='Acute headache'
        ),
        target=Coding(
            system=system,
            code='25064002',
            display='Headache'
        )
    )

    eq_(exp, res)
