#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `EmptyCitationAttributeUpdator` class."""

import os
import tempfile
import shutil

import unittest
import mock
from mock import MagicMock

from ndexncipidloader.loadndexncipidloader import EmptyCitationAttributeUpdator
from ndex2.nice_cx_network import NiceCXNetwork

class TestEmptyCitationAttributeRemover(unittest.TestCase):
    """Tests for `EmptyCitationAttributeUpdator` class."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_get_description(self):
        updator = EmptyCitationAttributeUpdator()
        self.assertTrue('Removes empty and' in updator.get_description())

    def test_update_none_passed_in(self):
        updator = EmptyCitationAttributeUpdator()
        self.assertEqual(['Network is None'], updator.update(None))

    def test_edge_with_no_edgecitation(self):
        updator = EmptyCitationAttributeUpdator()
        net = NiceCXNetwork()
        edgeid = net.create_edge(edge_source=0, edge_target=1,
                                 edge_interaction='foo')
        self.assertEqual([], updator.update(net))
        edge = net.get_edge_attribute(edgeid, 'citation')
        self.assertEqual([], edge['v'])
        self.assertEqual('list_of_string', edge['d'])

    def test_edge_with_emptypubmedcitation(self):
        updator = EmptyCitationAttributeUpdator()
        net = NiceCXNetwork()
        edgeid = net.create_edge(edge_source=0, edge_target=1,
                                 edge_interaction='foo')
        net.set_edge_attribute(edgeid, 'citation', values=['pubmed:'],
                               type='list_of_string')
        self.assertEqual([], updator.update(net))
        edge = net.get_edge_attribute(edgeid, 'citation')
        self.assertEqual([], edge['v'])

    def test_edge_with_emptylistcitation(self):
        updator = EmptyCitationAttributeUpdator()
        net = NiceCXNetwork()
        edgeid = net.create_edge(edge_source=0, edge_target=1,
                                 edge_interaction='foo')
        net.set_edge_attribute(edgeid, 'citation', values=[],
                               type='list_of_string')
        self.assertEqual([], updator.update(net))
        edge = net.get_edge_attribute(edgeid, 'citation')
        self.assertEqual([], edge['v'])

    def test_edge_with_emptystring(self):
        updator = EmptyCitationAttributeUpdator()
        net = NiceCXNetwork()
        edgeid = net.create_edge(edge_source=0, edge_target=1,
                                 edge_interaction='foo')
        net.set_edge_attribute(edgeid, 'citation', values=[''],
                               type='list_of_string')
        self.assertEqual([], updator.update(net))
        edge = net.get_edge_attribute(edgeid, 'citation')
        self.assertEqual([], edge['v'])

    def test_edge_with_emptyelementincitationlist(self):
        updator = EmptyCitationAttributeUpdator()
        net = NiceCXNetwork()
        edgeid = net.create_edge(edge_source=0, edge_target=1,
                                 edge_interaction='foo')
        net.set_edge_attribute(edgeid, 'citation',
                               values=['foo', 'pubmed:', 'hi'],
                               type='list_of_string')
        self.assertEqual([], updator.update(net))
        self.assertEqual(['foo', 'hi'],
                         net.get_edge_attribute(edgeid, 'citation')['v'])
