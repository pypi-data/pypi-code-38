#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `DirectEdgeAttributeUpdator` class."""

import os
import tempfile
import shutil

import unittest
from ndex2.nice_cx_network import NiceCXNetwork
from ndexsignorloader.ndexloadsignor import DirectEdgeAttributeUpdator


class TestDirectEdgeAttributeUpdator(unittest.TestCase):
    """Tests for `DirectEdgeAttributeUpdator` class."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_get_description(self):
        updator = DirectEdgeAttributeUpdator()
        self.assertEqual('Updates value of directed edge attribute to '
                         'true and false',
                         updator.get_description())

    def test_update_network_is_none(self):
        updator = DirectEdgeAttributeUpdator()
        self.assertEqual(['network is None'],
                         updator.update(None))

    def test_update_network_empty(self):
        updator = DirectEdgeAttributeUpdator()
        net = NiceCXNetwork()
        self.assertEqual([],
                         updator.update(net))

    def test_update_network_containing_all_types(self):
        updator = DirectEdgeAttributeUpdator()
        net = NiceCXNetwork()

        noattredge = net.create_edge(edge_source=0, edge_target=1,
                                     edge_interaction='foo')
        t_edge = net.create_edge(edge_source=2, edge_target=3,
                                 edge_interaction='blah')
        net.set_edge_attribute(t_edge,
                               DirectEdgeAttributeUpdator.DIRECTED_ATTRIB,
                               't', type='string')

        f_edge = net.create_edge(edge_source=3, edge_target=4,
                                 edge_interaction='blah')
        net.set_edge_attribute(f_edge,
                               DirectEdgeAttributeUpdator.DIRECTED_ATTRIB,
                               'f', type='string')

        o_edge = net.create_edge(edge_source=3, edge_target=4,
                                 edge_interaction='blah')
        net.set_edge_attribute(o_edge,
                               DirectEdgeAttributeUpdator.DIRECTED_ATTRIB,
                               'blah', type='string')
        self.assertEqual([],
                         updator.update(net))

        d_attrib = DirectEdgeAttributeUpdator.DIRECTED_ATTRIB
        res = net.get_edge_attribute(noattredge, d_attrib)
        self.assertEqual((None, None), res)

        res = net.get_edge_attribute(t_edge, d_attrib)
        self.assertEqual(res['v'], True)

        res = net.get_edge_attribute(f_edge, d_attrib)
        self.assertEqual(res['v'], False)

        res = net.get_edge_attribute(o_edge, d_attrib)
        self.assertEqual(res['v'], False)




