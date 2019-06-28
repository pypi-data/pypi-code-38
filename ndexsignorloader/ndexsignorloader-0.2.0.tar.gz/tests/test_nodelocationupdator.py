#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `NodeLocationUpdator` class."""

import os
import tempfile
import shutil

import unittest
from ndex2.nice_cx_network import NiceCXNetwork
from ndexsignorloader.ndexloadsignor import NodeLocationUpdator


class TestNodeLocationUpdator(unittest.TestCase):
    """Tests for `NodeLocationUpdator` class."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_get_description(self):
        updator = NodeLocationUpdator()
        self.assertEqual('Replace any empty node location attribute '
                         'values with cytoplasm',
                         updator.get_description())

    def test_update_network_is_none(self):
        updator = NodeLocationUpdator()
        self.assertEqual(['network is None'],
                         updator.update(None))

    def test_update_network_empty(self):
        updator = NodeLocationUpdator()
        net = NiceCXNetwork()
        self.assertEqual([],
                         updator.update(net))

    def test_update_network_containing_all_types(self):
        updator = NodeLocationUpdator()
        net = NiceCXNetwork()

        comp_attr = NodeLocationUpdator.LOCATION
        no_attr = net.create_node('somenode', node_represents='rep1')

        e_attr = net.create_node('somenode2',
                                 node_represents='uniprot:rep2')
        net.set_node_attribute(e_attr,
                               NodeLocationUpdator.LOCATION,
                               '')

        o_attr = net.create_node('somenode2',
                                 node_represents='uniprot:rep2')
        net.set_node_attribute(o_attr,
                               NodeLocationUpdator.LOCATION,
                               'blah')

        self.assertEqual([],
                         updator.update(net))

        self.assertEqual(NodeLocationUpdator.CYTOPLASM,
                         net.get_node_attribute(no_attr, comp_attr)['v'])

        self.assertEqual(NodeLocationUpdator.CYTOPLASM,
                         net.get_node_attribute(e_attr, comp_attr)['v'])

        self.assertEqual('blah',
                         net.get_node_attribute(o_attr, comp_attr)['v'])
