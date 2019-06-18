"""Verifies the 'gsea.py' module"""

from argparse import Namespace

import pkg_resources

from nose.tools import eq_, ok_, raises

from termlink.gsea import execute, _to_relationship
from termlink.models import Coding, Relationship

def test_execute():
    "Tests the conversion of a 'msigdb.*.symbols.gmt' file"
    path = pkg_resources.resource_filename(__name__, "resources/msigdb.test.symbols.gmt")
    uri = f"file://{path}"
    output = execute(Namespace(uri=uri))
    ok_(len(output) > 0)

@raises(ValueError)
def test_uri_scheme():
    """A URI scheme of 'file://' is required"""
    execute(Namespace(uri='foo://bar'))


@raises(ValueError)
def test_uri_filename_database():
    "A invalid file name throws a ValueError"
    execute(Namespace(uri='file:///invalid.foo.bar.symbols.gmt'))


@raises(ValueError)
def test_uri_filename_type():
    "A invalid file name throws a ValueError"
    execute(Namespace(uri='file:///msigdb.foo.bar.invalid.gmt'))


@raises(ValueError)
def test_uri_filename_suffix():
    "A invalid file name throws a ValueError"
    execute(Namespace(uri='file:///msigdb.foo.bar.symbols.invalid'))


def test_to_relationship():
    "A record is converted to an index"
    rec = ['target', 'source']
    idx = 1
    relationship = _to_relationship(rec, idx, equivalence='subsumes')
    eq_(relationship, Relationship(
        equivalence='subsumes',
        source=Coding(
            system="http://www.broadinstitute.org/gsea/msigdb",
            code='source',
            display='source'
        ),
        target=Coding(
            system="http://www.broadinstitute.org/gsea/msigdb",
            code='target',
            display='target'
        )
    ))

