#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `InvalidEdgeCitationRemover` class."""

import os
import tempfile
import shutil

import unittest
from ndex2.nice_cx_network import NiceCXNetwork
from ndexsignorloader.ndexloadsignor import InvalidEdgeCitationRemover


class TestInvalidEdgeCitationRemover(unittest.TestCase):
    """Tests for `InvalidEdgeCitationRemover` class."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_get_description(self):
        updator = InvalidEdgeCitationRemover()
        self.assertEqual('Removes any negative and non-numeric edge citations',
                         updator.get_description())

    def test_update_network_is_none(self):
        updator = InvalidEdgeCitationRemover()
        self.assertEqual(['network is None'],
                         updator.update(None))

    def test_update_network_empty(self):
        updator = InvalidEdgeCitationRemover()
        net = NiceCXNetwork()
        self.assertEqual([],
                         updator.update(net))

    def test_update_network_containing_several_citations(self):
        updator = InvalidEdgeCitationRemover()
        net = NiceCXNetwork()

        noattredge = net.create_edge(edge_source=0, edge_target=1,
                                     edge_interaction='foo')
        t_edge = net.create_edge(edge_source=2, edge_target=3,
                                 edge_interaction='blah')
        net.set_edge_attribute(t_edge,
                               InvalidEdgeCitationRemover.CITATION_ATTRIB,
                               [], type='list_of_string')

        v_edge = net.create_edge(edge_source=3, edge_target=4,
                                 edge_interaction='blah')
        net.set_edge_attribute(v_edge,
                               InvalidEdgeCitationRemover.CITATION_ATTRIB,
                               ['pubmed:1234'], type='list_of_string')

        o_edge = net.create_edge(edge_source=3, edge_target=4,
                                 edge_interaction='blah')
        net.set_edge_attribute(o_edge,
                               InvalidEdgeCitationRemover.CITATION_ATTRIB,
                               ['pubmed:Other'], type='list_of_string')

        neg_edge = net.create_edge(edge_source=5, edge_target=6,
                                   edge_interaction='blah')

        net.set_edge_attribute(neg_edge,
                               InvalidEdgeCitationRemover.CITATION_ATTRIB,
                               ['pubmed:-100', 'pubmed:5'],
                               type='list_of_string')

        issues = updator.update(net)
        self.assertEqual(2, len(issues))
        self.assertTrue('Removing invalid citation id: '
                        'pubmed:Other on edge id: ' + str(o_edge) in
                        issues)
        self.assertTrue('Removing invalid citation id: '
                        'pubmed:-100 on edge id: ' + str(neg_edge) in
                        issues)

        d_attrib = InvalidEdgeCitationRemover.CITATION_ATTRIB
        res = net.get_edge_attribute(noattredge, d_attrib)
        self.assertEqual((None, None), res)

        res = net.get_edge_attribute(t_edge, d_attrib)
        self.assertEqual([], res['v'])

        res = net.get_edge_attribute(v_edge, d_attrib)
        self.assertEqual(['pubmed:1234'], res['v'])

        res = net.get_edge_attribute(o_edge, d_attrib)
        self.assertEqual([], res['v'])

        res = net.get_edge_attribute(neg_edge, d_attrib)
        self.assertEqual(['pubmed:5'], res['v'])

    def test_update_network_with_pmc_citation(self):
        updator = InvalidEdgeCitationRemover()
        net = NiceCXNetwork()

        noattredge = net.create_edge(edge_source=0, edge_target=1,
                                     edge_interaction='foo')
        t_edge = net.create_edge(edge_source=2, edge_target=3,
                                 edge_interaction='blah')
        net.set_edge_attribute(t_edge,
                               InvalidEdgeCitationRemover.CITATION_ATTRIB,
                               ['pubmed:PMC3619734'], type='list_of_string')

        issues = updator.update(net)
        self.assertEqual(1, len(issues))
        self.assertTrue('Replacing' in issues[0])

        res = net.get_edge_attribute(t_edge,
                                     InvalidEdgeCitationRemover.CITATION_ATTRIB)
        self.assertEqual(['pubmed:15109499'], res['v'])




