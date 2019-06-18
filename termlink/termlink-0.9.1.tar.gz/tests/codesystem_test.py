"""Verifies the 'codesystem.py' module"""

from argparse import Namespace

import pkg_resources

from nose.tools import eq_, ok_, raises

from pronto import Term

from termlink.codesystem import _get_relationships, execute
from termlink.models import Coding, Relationship

@raises(ValueError)
def test_uri_scheme():
    """An unsupported URI scheme throws a ValueError"""
    execute(Namespace(uri='foo://bar'))

def test_json_format():
    """Tests the conversion of an .json file"""
    path = pkg_resources.resource_filename(__name__, "resources/codesystem.json")
    uri = f"file://{path}"
    output = execute(Namespace(uri=uri))
    ok_(len(output) > 0)
