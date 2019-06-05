import unittest
from unittest import TestCase

from network_extensions.igraphx import multilayer


class TestSubNetwork(TestCase):
    def test_createSubNetwork_1(self):
        layers = ["person_person_met"]

        ml2 = multilayer.MultiLayerGraph.load("data/multilayer_GR_merged_only_nodes_in_year.pickle")
        sn = ml2.createSubNetwork(layers)

        self.assertEqual(len(sn), 1)

        self.assertEqual(len(sn.ynws), len(ml2.ynws))
        self.assertEqual(len(sn.merged_ynws),len(ml2.merged_ynws))
        self.assertEqual(len(sn.merged_ynws[-100].ynws),len(ml2.merged_ynws[-100].ynws))

    def test_createSubNetwork_2(self):
        layers = ["person_person_met","person","institution","person_institution"]

        ml2 = multilayer.MultiLayerGraph.load("data/multilayer_GR_merged_only_nodes_in_year.pickle")
        sn = ml2.createSubNetwork(layers)

        self.assertEqual(len(sn), 1)

        self.assertEqual(len(sn.ynws), len(ml2.ynws))
        self.assertEqual(len(sn.merged_ynws), len(ml2.merged_ynws))
        self.assertEqual(len(sn.merged_ynws[-100].ynws), len(ml2.merged_ynws[-100].ynws))

