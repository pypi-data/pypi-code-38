#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `SpringLayoutUpdator` class."""

import os
import tempfile
import shutil

import unittest
from ndex2.nice_cx_network import NiceCXNetwork
from ndexsignorloader.ndexloadsignor import SpringLayoutUpdator
from ndexsignorloader.ndexloadsignor import NodeLocationUpdator


class TestSpringLayoutUpdator(unittest.TestCase):
    """Tests for `UpdatePrefixesForNodeRepresents` class."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_get_description(self):
        updator = SpringLayoutUpdator()
        self.assertEqual('Applies Spring layout to network',
                         updator.get_description())

    def test_update_network_is_none(self):
        updator = SpringLayoutUpdator()
        self.assertEqual(['network is None'],
                         updator.update(None))

    def test_update_network_empty(self):
        updator = SpringLayoutUpdator()
        net = NiceCXNetwork()
        self.assertEqual([],
                         updator.update(net))

    def test_update_network_containing_all_types(self):
        updator = SpringLayoutUpdator()
        net = NiceCXNetwork()

        comp_attr = NodeLocationUpdator.LOCATION
        ecnode = net.create_node(node_name='ecnode', node_represents='ecnoder')
        net.set_node_attribute(ecnode, comp_attr,
                               SpringLayoutUpdator.EXTRACELLULAR)

        rnode = net.create_node(node_name='rnode', node_represents='rnoder')
        net.set_node_attribute(rnode, comp_attr,
                               SpringLayoutUpdator.RECEPTOR)

        cnode = net.create_node(node_name='cnode', node_represents='cnoder')
        net.set_node_attribute(cnode, comp_attr,
                               SpringLayoutUpdator.CYTOPLASM)

        fnode = net.create_node(node_name='fnode', node_represents='fnoder')
        net.set_node_attribute(fnode, comp_attr,
                               SpringLayoutUpdator.FACTOR)

        pnode = net.create_node(node_name='pnode', node_represents='pnoder')
        net.set_node_attribute(pnode, comp_attr,
                               SpringLayoutUpdator.PHENOTYPESLIST)

        xnode = net.create_node(node_name='xnode', node_represents='xnoder')
        self.assertEqual([], updator.update(net))

        res = net.get_opaque_aspect(SpringLayoutUpdator.CARTESIAN_LAYOUT)

        ydict = {}
        for entry in res:
            ydict[entry['node']] = entry['y']
        self.assertTrue(ydict[ecnode] < 0.0)
        self.assertTrue(ydict[rnode] < 0.0)
        self.assertTrue(ydict[cnode] > -100.0)

        self.assertTrue(ydict[fnode] > 0.0)
        self.assertTrue(ydict[pnode] > 0.0)





