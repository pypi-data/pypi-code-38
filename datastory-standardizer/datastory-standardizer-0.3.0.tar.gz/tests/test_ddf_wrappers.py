import io
import os
import unittest
import pandas as pd
import standardizer as sd


class TestMergePackages(unittest.TestCase):
    def setUp(self):
        testdir = os.path.dirname(os.path.abspath(__file__))
        package = os.path.join(testdir, "testddf1")
        self.package = sd.merge.DDFPackage(package)

    def test_contains(self):
        self.assertTrue("gpd_cusd" in self.package)

    def test_not_contains(self):
        self.assertFalse("thizwilnevahbeconceptz" in self.package)

    def test_filter_concepts_frame(self):
        df = "concept,concept_type\n" "con_a,measure\n" "con_b,entity_domain"

        df = pd.read_csv(io.StringIO(df))
        df = sd.merge.filter_items(df, include=["con_a"])
        self.assertFalse((df.concept == "con_b").any())
