#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `UpdatePrefixesForNodeRepresents` class."""

import os
import tempfile
import shutil

import unittest
from ndex2.nice_cx_network import NiceCXNetwork
from ndexsignorloader.ndexloadsignor import UpdatePrefixesForNodeRepresents


class TestUpdatePrefixesForNodeRepresents(unittest.TestCase):
    """Tests for `UpdatePrefixesForNodeRepresents` class."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_get_description(self):
        updator = UpdatePrefixesForNodeRepresents()
        self.assertEqual('Updates value of DIRECT edge attribute to yes '
                         'and no',
                         updator.get_description())

    def test_update_network_is_none(self):
        updator = UpdatePrefixesForNodeRepresents()
        self.assertEqual(['network is None'],
                         updator.update(None))

    def test_update_network_empty(self):
        updator = UpdatePrefixesForNodeRepresents()
        net = NiceCXNetwork()
        self.assertEqual([],
                         updator.update(net))

    def test_update_network_containing_all_types(self):
        updator = UpdatePrefixesForNodeRepresents()
        net = NiceCXNetwork()

        uni_one = net.create_node('somenode', node_represents='rep1')
        net.set_node_attribute(uni_one, 'DATABASE', 'UNIPROT')

        uni_two = net.create_node('somenode2',
                                  node_represents='uniprot:rep2')
        net.set_node_attribute(uni_two, 'DATABASE', 'UNIPROT')

        sig_one = net.create_node('somenode3', node_represents='rep3')
        net.set_node_attribute(sig_one, 'DATABASE', 'SIGNOR')

        sig_two = net.create_node('somenode4', node_represents='signor:rep4')
        net.set_node_attribute(sig_two, 'DATABASE', 'SIGNOR')

        other = net.create_node('somenode5',
                                node_represents='blah:rep5')
        net.set_node_attribute(other, 'DATABASE', 'other')

        self.assertEqual([],
                         updator.update(net))

        res = net.get_node(uni_one)
        self.assertEqual('uniprot:rep1', res['r'])
        self.assertEqual(None,
                         net.get_node_attribute(uni_one, 'DATABASE'))

        res = net.get_node(uni_two)
        self.assertEqual('uniprot:rep2', res['r'])
        self.assertEqual(None,
                         net.get_node_attribute(uni_two, 'DATABASE'))

        res = net.get_node(sig_one)
        self.assertEqual('signor:rep3', res['r'])
        self.assertEqual(None,
                         net.get_node_attribute(sig_one, 'DATABASE'))

        res = net.get_node(sig_two)
        self.assertEqual('signor:rep4', res['r'])
        self.assertEqual(None,
                         net.get_node_attribute(sig_two, 'DATABASE'))

        res = net.get_node(other)
        self.assertEqual('blah:rep5', res['r'])
        self.assertEqual(None,
                         net.get_node_attribute(other, 'DATABASE'))







