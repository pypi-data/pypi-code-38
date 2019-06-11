#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `UniProtToGeneSymbolUpdater` class."""

import os
import tempfile
import shutil

import unittest
import mock
from mock import MagicMock
from ndex2.nice_cx_network import NiceCXNetwork
from ndexncipidloader.loadndexncipidloader import UniProtToGeneSymbolUpdater


class TestUniProtToGeneSymbolUpdater(unittest.TestCase):
    """Tests for `UniProtToGeneSymbolUpdater` class."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_update_none_passed_in(self):
        updater = UniProtToGeneSymbolUpdater()
        self.assertTrue('Replacement of uniprot' in updater.get_description())
        self.assertEqual(None, updater.update(None))

    def test_update_no_represents_in_nodes(self):
        updater = UniProtToGeneSymbolUpdater()
        net = NiceCXNetwork()
        nodeone = net.create_node(node_name='node1', node_represents=None)
        nodetwo = net.create_node(node_name='node2', node_represents=None)

        # so in NDEx2 python client 3.2.0 and earlier if you
        # pass node_represents=None the represents field is set
        # to the values set in node_name which doesn't seem like
        # correct behavior...
        firstnode = net.get_node(nodeone)
        del firstnode['r']
        secondnode = net.get_node(nodetwo)
        del secondnode['r']

        res = updater.update(net)
        self.assertEqual(2, len(res))
        self.assertTrue('(0) and name (node1) no represents' in res[0])
        self.assertTrue('(1) and name (node2) no represents' in res[1])
        self.assertEqual('node1', net.get_node(nodeone)['n'])
        self.assertEqual('node2', net.get_node(nodetwo)['n'])

    def test_update_no_nodes_start_with_uniprot(self):
        updater = UniProtToGeneSymbolUpdater()
        net = NiceCXNetwork()
        nodeone = net.create_node(node_name='node1', node_represents='node1')
        nodetwo = net.create_node(node_name='node2', node_represents='node2')
        res = updater.update(net)
        self.assertEqual(0, len(res))
        self.assertEqual('node1', net.get_node(nodeone)['n'])
        self.assertEqual('node2', net.get_node(nodetwo)['n'])

    def test_update_one_node_to_update_symbol_not_none(self):
        mock = MagicMock()
        mock.get_symbol = MagicMock(return_value='SMILE')
        updater = UniProtToGeneSymbolUpdater(searcher=mock)
        net = NiceCXNetwork()

        nodeone = net.create_node(node_name='Q1', node_represents='uniprot:q1')
        res = updater.update(net)
        self.assertEqual(0, len(res))
        self.assertEqual('SMILE', net.get_node(nodeone)['n'])
        self.assertEqual('uniprot:q1', net.get_node(nodeone)['r'])

        mock.get_symbol.assert_called_with('Q1')

    def test_update_one_node_to_update_symbol_is_none(self):
        mock = MagicMock()
        mock.get_symbol = MagicMock(return_value=None)
        updater = UniProtToGeneSymbolUpdater(searcher=mock)
        net = NiceCXNetwork()

        nodeone = net.create_node(node_name='bob', node_represents='uniprot:bob')
        res = updater.update(net)
        self.assertEqual(1, len(res))
        self.assertTrue('No symbol found to replace' in res[0])
        self.assertEqual('bob', net.get_node(nodeone)['n'])
        self.assertEqual('uniprot:bob', net.get_node(nodeone)['r'])

        mock.get_symbol.assert_called_with('bob')
