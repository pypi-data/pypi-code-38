# -*- coding: utf-8 -*-
"""
Doctest runner for 'ftw.recipe.solr'.
"""
__docformat__ = 'restructuredtext'

import unittest
import zc.buildout.tests
import zc.buildout.testing
import doctest
import re
import os.path

from zope.testing import renormalizing

optionflags = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE |
               doctest.REPORT_ONLY_FIRST_FAILURE)


# same as zc.buildout.testing.normalize_path
# but equal sign (=) may not be part of a path
def _normalize_path(match):
    path = match.group(1)
    if os.path.sep == '\\':
        path = path.replace('\\\\', '/')
        if path.startswith('\\'):
            path = path[1:]
    return '/' + path.replace(os.path.sep, '/')

normalize_path = (
    re.compile(
        r'''[^'" \t\n\r=]+\%(sep)s_[Tt][Ee][Ss][Tt]_\%(sep)s([^"' \t\n\r]+)'''
        % dict(sep=os.path.sep)),
    _normalize_path,
    )


def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)

    # Install any other eggs that should be available in the tests
    zc.buildout.testing.install_develop('zc.recipe.egg', test)
    zc.buildout.testing.install_develop('jinja2', test)
    zc.buildout.testing.install_develop('MarkupSafe', test)

    # Install the recipe in develop mode
    zc.buildout.testing.install_develop('ftw.recipe.solr', test)


def test_suite():
    suite = unittest.TestSuite((doctest.DocFileSuite(
        'README.txt',
        setUp=setUp,
        tearDown=zc.buildout.testing.buildoutTearDown,
        optionflags=optionflags,
        checker=renormalizing.RENormalizing([
            # If want to clean up the doctest output you
            # can register additional regexp normalizers
            # here. The format is a two-tuple with the RE
            # as the first item and the replacement as the
            # second item, e.g.
            # (re.compile('my-[rR]eg[eE]ps'), 'my-regexps')
            normalize_path,
            (re.compile(r'http://localhost:\d+'), 'http://test.server'),
            (re.compile("Not found: .*buildouttests/[a-zA-Z0-9.]+/\n"), ''),
            ]),
    )))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
