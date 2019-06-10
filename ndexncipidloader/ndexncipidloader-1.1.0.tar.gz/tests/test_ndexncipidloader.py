#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `NDExNciPidLoader` class."""

import os
import tempfile
import shutil

import unittest
import mock
from mock import MagicMock
from ndex2.nice_cx_network import NiceCXNetwork

import ndexncipidloader
from ndexncipidloader.loadndexncipidloader import NDExNciPidLoader
from ndexncipidloader.loadndexncipidloader import NetworkIssueReport
from ndexutil.config import NDExUtilConfig
from ndexncipidloader import loadndexncipidloader


class Param(object):
    """
    Dummy object
    """
    pass


class TestNDExNciPidLoader(unittest.TestCase):
    """Tests for `NDExNciPidLoader` class."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_parse_config(self):

        temp_dir = tempfile.mkdtemp()
        try:
            p = Param()
            p.profile = 'foo'
            conf = os.path.join(temp_dir, 'blah.conf')
            p.conf = conf
            with open(conf, 'w') as f:
                f.write('[' + p.profile + ']' + '\n')
                f.write(NDExUtilConfig.USER + ' = bob\n')
                f.write(NDExUtilConfig.PASSWORD + ' = pass\n')
                f.write(NDExUtilConfig.SERVER + ' = server\n')
                f.flush()

            loader = NDExNciPidLoader(p)
            loader._parse_config()
            self.assertEqual('bob', loader._user)
            self.assertEqual('pass', loader._pass)
            self.assertEqual('server', loader._server)
        finally:
            shutil.rmtree(temp_dir)

    def test_parse_load_plan(self):
        p = Param()
        p.loadplan = loadndexncipidloader.get_load_plan()
        loader = NDExNciPidLoader(p)
        loader._parse_load_plan()
        self.assertTrue(isinstance(loader._loadplan, dict))

    def test_get_style_template(self):
        p = Param()
        p.style = loadndexncipidloader.get_style()
        loader = NDExNciPidLoader(p)
        loader._load_style_template()
        self.assertTrue(loader._template is not None)

    def test_normalize_context_prefixes(self):
        loader = NDExNciPidLoader(None)
        self.assertEqual(None,
                         loader._normalize_context_prefixes(None))

        # try with value that shouldn't change
        self.assertEqual('foo',
                         loader._normalize_context_prefixes('foo'))

        # try uniprot knowledgebase:
        self.assertEqual('uniprot:hi',
                         loader._normalize_context_prefixes('uniprot '
                                                            'knowledgebase:'
                                                            'hi'))
        # try kegg compound:
        self.assertEqual('kegg.compound:hi',
                         loader._normalize_context_prefixes('kegg compound:'
                                                            'hi'))
        # try UniProt:
        self.assertEqual('uniprot:yo',
                         loader._normalize_context_prefixes('UniProt:'
                                                            'yo'))

    def test_set_wasderivedfrom(self):
        net = NiceCXNetwork()
        net.set_name('foo')
        loader = NDExNciPidLoader(None)
        loader._set_wasderivedfrom(net)
        derived_attr = loadndexncipidloader.DERIVED_FROM_ATTRIB
        self.assertEqual('<a href="ftp://' +
                         loadndexncipidloader.DEFAULT_FTP_HOST +
                         '/' + loadndexncipidloader.DEFAULT_FTP_DIR + '/' +
                         'foo.owl.gz">foo.owl.gz</a>',
                         net.get_network_attribute(derived_attr)['v'])

    def test_set_normalizationversion(self):
        net = NiceCXNetwork()
        net.set_name('foo')
        loader = NDExNciPidLoader(None)
        loader._set_normalization_version(net)
        norm_attr = loadndexncipidloader.NORMALIZATIONVERSION_ATTRIB
        self.assertEqual('0.1',
                         net.get_network_attribute(norm_attr)['v'])

    def test_set_generatedby_in_network_attributes(self):
        net = NiceCXNetwork()
        net.set_name('foo')
        loader = NDExNciPidLoader(None)
        loader._set_generatedby_in_network_attributes(net)
        norm_attr = loadndexncipidloader.GENERATED_BY_ATTRIB
        self.assertTrue(' ' + str(ndexncipidloader.__version__) in
                        net.get_network_attribute(norm_attr)['v'])

    def test_add_node_types_in_network_to_report_empty_network(self):
        loader = NDExNciPidLoader(None)
        report = NetworkIssueReport('foo')
        net = NiceCXNetwork()
        net.set_name('foo')
        loader._add_node_types_in_network_to_report(net, report)
        self.assertEqual(set(), report.get_nodetypes())
