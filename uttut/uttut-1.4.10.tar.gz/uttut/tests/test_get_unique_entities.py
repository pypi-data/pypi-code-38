# -*- coding: utf-8 -*-
from unittest import TestCase

from uttut.elements import (
    Datum,
    Intent,
    Entity,
)
from ..get_unique_entities import (
    get_unique_entities,
)


class GetUniqueEntitiesTestCase(TestCase):

    def setUp(self):
        self.intents = [Intent(0)]
        self.entities = [
            Entity(label=1, value='豪大', start=7, end=9,
                   replacements=['肯德基', '麥噹噹']),
            Entity(label=2, value='雞排', start=9, end=11,
                   replacements=['漢堡', '薯條', '滷肉飯']),
        ]
        self.example_datum = Datum(
            utterance='家豪大大喜歡吃豪大雞排',
            intents=self.intents,
            entities=self.entities,
        )

    def test_get_unique_entities(self):
        result = get_unique_entities(data=[self.example_datum])
        self.assertEqual(set([1, 2]), set(result))
