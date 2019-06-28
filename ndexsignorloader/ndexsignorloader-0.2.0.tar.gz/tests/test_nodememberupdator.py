#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `NodeMemberUpdator` class."""

import os
import tempfile
import shutil
from mock import MagicMock

import unittest
from ndex2.nice_cx_network import NiceCXNetwork
from ndexsignorloader.ndexloadsignor import NodeMemberUpdator
from ndexutil.tsv.loaderutils import GeneSymbolSearcher


class TestNodeMemberUpdator(unittest.TestCase):
    """Tests for `NodeMemberUpdator` class."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_get_description(self):
        updator = NodeMemberUpdator(None, None)
        self.assertEqual('Add genes to member node attribute for complexes '
                         'and protein families',
                         updator.get_description())

    def test_replace_signor_ids(self):
        pfdict = {'a': ['2', '3'], 'SIGNOR-PF10': ['7', '8']}
        cdict =  {'e': ['5', '6'], 'SIGNOR-C1': ['9', '10']}
        updator = NodeMemberUpdator(pfdict, cdict)
        res = updator._replace_signor_ids(['a',
                                           'SIGNOR-PF10',
                                           'SIGNOR-PF9',
                                           'e',
                                           'SIGNOR-C1',
                                           'SIGNOR-C2'])
        res[0].sort()
        self.assertEqual(['10', '7', '8', '9', 'a', 'e'], res[0])
        self.assertEqual(2, len(res[1]))
        self.assertTrue('Protein id: SIGNOR-PF9 matched prefix'
                        ' SIGNOR-PF which is assumed to be a reference to another entry, but none found. Skipping.' in res[1])
        self.assertTrue('Protein id: SIGNOR-C2 matched prefix'
                        ' SIGNOR-C which is assumed to be a reference to another entry, but none found. Skipping.' in
                        res[1])

    def test_update_network_is_none(self):
        updator = NodeMemberUpdator(None, None)
        self.assertEqual(['network is None'],
                         updator.update(None))

    def test_update_network_empty(self):
        updator = NodeMemberUpdator(None, None)
        net = NiceCXNetwork()
        self.assertEqual([],
                         updator.update(net))

    def test_add_member_genes(self):

        net = NiceCXNetwork()
        aid = net.create_node('a')
        net.set_node_attribute(aid, NodeMemberUpdator.TYPE, 'proteinfamily')

        notinid = net.create_node('x')
        net.set_node_attribute(notinid, NodeMemberUpdator.TYPE, 'proteinfamily')

        mock = GeneSymbolSearcher(bclient=None)
        mock.get_symbol = MagicMock(side_effect=['', None])
        updator = NodeMemberUpdator(None, None,
                                    genesearcher=mock)

        aidnode = net.get_node(aid)
        res = updator._add_member_genes(net, aidnode, [])
        self.assertEqual(['No proteins obtained for node: ' + str(aidnode)], res)

        notinidnode = net.get_node(notinid)
        res = updator._add_member_genes(net, notinidnode, ['x'])
        self.assertTrue('For node ' + str(notinidnode) +
                        ' No gene symbol found for x. Skipping.' in res)

        self.assertTrue('Not a single gene symbol found. Skipping insertion '
                        'of member attribute for node ' + str(notinidnode) in res)

    def test_update_network_containing_all_types(self):
        pfdict = {'a': ['2', '3'], 'SIGNOR-PF10': ['7', '8']}
        cdict = {'e': ['5', '6'], 'SIGNOR-C1': ['9', '10']}

        net = NiceCXNetwork()
        aid = net.create_node('a')
        net.set_node_attribute(aid, NodeMemberUpdator.TYPE, 'proteinfamily')

        eid = net.create_node('e')
        net.set_node_attribute(eid, NodeMemberUpdator.TYPE, 'complex')

        oid = net.create_node('c')

        o2id = net.create_node('d')
        net.set_node_attribute(o2id, NodeMemberUpdator.TYPE, 'protein')

        notinid = net.create_node('x')
        net.set_node_attribute(notinid, NodeMemberUpdator.TYPE, 'proteinfamily')

        notinid2 = net.create_node('y')
        net.set_node_attribute(notinid2, NodeMemberUpdator.TYPE, 'complex')

        mock = GeneSymbolSearcher(bclient=None)
        mock.get_symbol = MagicMock(side_effect=['AA', 'BB', 'CC', 'DD'])
        updator = NodeMemberUpdator(pfdict, cdict,
                                    genesearcher=mock)
        res = updator.update(net)
        self.assertTrue("No entry in proteinfamily map for node: {'@id': 4, 'n': 'x', 'r': 'x'}" in res)
        self.assertTrue("No entry in complexes map for node: {'@id': 5, 'n': 'y', 'r': 'y'}" in res)

        res = net.get_node_attribute(aid, NodeMemberUpdator.MEMBER)
        self.assertTrue('hgnc.symbol:AA' in res['v'])
        self.assertTrue('hgnc.symbol:BB' in res['v'])

        res = net.get_node_attribute(eid, NodeMemberUpdator.MEMBER)
        self.assertTrue('hgnc.symbol:CC' in res['v'])
        self.assertTrue('hgnc.symbol:DD' in res['v'])

        res = net.get_node_attribute(oid, NodeMemberUpdator.MEMBER)
        self.assertEqual(None, res)

        res = net.get_node_attribute(o2id, NodeMemberUpdator.MEMBER)
        self.assertEqual(None, res)
