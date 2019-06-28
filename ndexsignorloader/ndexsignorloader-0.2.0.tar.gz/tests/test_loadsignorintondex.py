#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `LoadSignorIntoNDex` class."""

import os
import tempfile
import shutil

import unittest
from ndexsignorloader.ndexloadsignor import LoadSignorIntoNDEx
from ndexsignorloader import ndexloadsignor
from ndex2.nice_cx_network import NiceCXNetwork


class FakeArgs(object):
    pass


class TestLoadSignorIntoNDex(unittest.TestCase):
    """Tests for `LoadSignorIntoNDex` class."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_wasderivedfrom(self):
        fargs = FakeArgs()
        fargs.conf = 'hi'
        fargs.profile = 'profile'
        fargs.datadir = '/foo'

        loader = LoadSignorIntoNDEx(fargs, None)
        net = NiceCXNetwork()
        loader._set_wasderivedfrom(net, 'foo')
        res = net.get_network_attribute(ndexloadsignor.DERIVED_FROM_ATTRIB)
        self.assertEqual('https://signor.uniroma2.it/pathway_browser.php?'
                         'organism=&pathway_list=foo', res['v'])

        # try with is_full_pathway false
        net = NiceCXNetwork()
        loader._set_wasderivedfrom(net, 'foo',
                                   is_full_pathway=False)
        res = net.get_network_attribute(ndexloadsignor.DERIVED_FROM_ATTRIB)
        self.assertEqual('https://signor.uniroma2.it/pathway_browser.php?'
                         'organism=&pathway_list=foo', res['v'])

        # try with is_full_pathway true
        net = NiceCXNetwork()
        loader._set_wasderivedfrom(net, 'foo',
                                   is_full_pathway=True)
        res = net.get_network_attribute(ndexloadsignor.DERIVED_FROM_ATTRIB)
        self.assertEqual('https://signor.uniroma2.it', res['v'])
