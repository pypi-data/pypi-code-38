import unittest
import os
from .taggeddataframe import TaggedDataFrame
from typing import List
from .coltag import ColTag
import pandas as pd

class TestTaggedDataFrame(unittest.TestCase):
    def setUp(self):
        dirname = os.path.dirname(__file__)
        self.dataset = pd.read_csv(dirname + "/resources/train.csv")

    def test_initializes_and_returns_tags(self):
        t:TaggedDataFrame =TaggedDataFrame(self.dataset)
        originals: List[str] = t.tagged_as(ColTag.original)
        self.assertEqual(len(self.dataset.columns.values), len(originals))

        modified: List[str] = t.tagged_as(ColTag.modified)
        self.assertEqual(0, len(modified))

    def test_tracks_and_returns_tags(self):
        t:TaggedDataFrame =TaggedDataFrame(self.dataset)
        t.tag_column("Cabin", ColTag.modified)
        modified: List[str] = t.tagged_as(ColTag.modified)
        self.assertEqual(1, len(modified))
        self.assertEqual("Cabin", modified[0])

        t.tag_column("Cabin", ColTag.modified)
        modified: List[str] = t.tagged_as(ColTag.modified)
        self.assertEqual(1, len(modified))

        t.tag_column("NewCol", ColTag.modified)
        modified: List[str] = t.tagged_as(ColTag.modified)
        self.assertEqual(2, len(modified))

        originals: List[str] = t.tagged_as(ColTag.original)
        self.assertEqual(len(self.dataset.columns.values), len(originals))

        mapping: List[str] = t.tagged_as(ColTag.mapping)
        self.assertEqual(0, len(mapping))

        t.tag_column("NewCol", ColTag.mapping)
        mapping: List[str] = t.tagged_as(ColTag.mapping)
        self.assertEqual(1, len(mapping))

    def test_advanced_column_retrival(self):
        t:TaggedDataFrame =TaggedDataFrame(self.dataset)
        t.tag_column("Cabin", ColTag.modified)
        self.assertEqual(
            len(self.dataset.columns.values) - 1, 
            len(t.retrive([ColTag.original], [ColTag.modified])),
        )

        t.tag_column("Age", ColTag.modified)

        self.assertEqual(
            len(self.dataset.columns.values) - 2, 
            len(t.retrive([ColTag.original], [ColTag.modified])),
        )
        self.assertEqual(
            2, 
            len(t.retrive([ColTag.modified])),
        )
        self.assertEqual(
            len(self.dataset.columns.values), 
            len(t.retrive([ColTag.original, ColTag.modified])),
        )

        t.tag_column("Sex", ColTag.categorized)

        self.assertEqual(
            3, 
            len(t.retrive([ColTag.modified, ColTag.categorized])),
        )
        self.assertEqual(
            0, 
            len(t.retrive([ColTag.modified, ColTag.categorized], [ColTag.original])),
        )

    def test_advanced_column_retrival_empty_list(self):
        t:TaggedDataFrame =TaggedDataFrame(self.dataset)
        self.assertEqual(
            len(self.dataset.columns.values), 
            len(t.retrive([])),
        )
    
        t.tag_column("Cabin", ColTag.modified)
        self.assertEqual(
            len(self.dataset.columns.values) - 1, 
            len(t.retrive([], [ColTag.modified])),
        )

    def test_column_removal(self):
        t:TaggedDataFrame =TaggedDataFrame(self.dataset)
        self.assertEqual(
            12, 
            len(t.retrive()),
        )
       
        t.remove(["Cabin", "Sex"])
        self.assertEqual(
            10, 
            len(t.retrive()),
        )

        self.assertRaises(KeyError, t.remove, ["Cabin"])




        

