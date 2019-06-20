from unittest import TestCase

from uttut.elements import Datum, Entity, Intent
from ..partition_by_entities import partition_by_entities


class PartitionByEntitiesTestCase(TestCase):

    def setUp(self):
        self.utterance = '我想訂明天從紐約飛到新加坡的機票'
        self.entities = [
            Entity(label=0, value='明天', start=3, end=5, replacements=['下禮拜二']),
            Entity(label=1, value='紐約', start=6, end=8),
            Entity(label=2, value='新加坡', start=10, end=13, replacements=['斯堪地那維亞', 'KIX']),
        ]
        self.intents = [
            Intent(label=0),
        ]
        self.datum = Datum(
            utterance=self.utterance,
            intents=self.intents,
            entities=self.entities,
        )

        self.datum_wo_entity = Datum(
            utterance='薄餡亂入',
            intents=[Intent(label=0)],
        )

    def test_partition_by_entities(self):
        actual_parts, entity_names = partition_by_entities(self.datum, False)
        expected_parts = [
            ['我想訂'],
            ['下禮拜二'],
            ['從'],
            ['紐約'],
            ['飛到'],
            ['斯堪地那維亞', 'KIX'],
            ['的機票'],
        ]
        for exp_part, act_part in zip(expected_parts, actual_parts):
            self.assertEqual(set(exp_part), set(act_part))
        self.assertEqual(
            entity_names,
            [None, 0, None, 1, None, 2, None],
        )

    def test_partition_by_entities_include_orig(self):
        actual_parts, entity_names = partition_by_entities(self.datum, True)
        expected_parts = [
            ['我想訂'],
            ['明天', '下禮拜二'],
            ['從'],
            ['紐約'],
            ['飛到'],
            ['新加坡', '斯堪地那維亞', 'KIX'],
            ['的機票'],
        ]
        for exp_part, act_part in zip(expected_parts, actual_parts):
            self.assertEqual(set(exp_part), set(act_part))
        self.assertEqual(
            entity_names,
            [None, 0, None, 1, None, 2, None],
        )

    def test_datum_wo_entity(self):
        # do not include origin
        output = partition_by_entities(self.datum_wo_entity, True)
        self.assertEqual(([['薄餡亂入']], [None]), output)

        # include origin
        output = partition_by_entities(self.datum_wo_entity, False)
        self.assertEqual(([['薄餡亂入']], [None]), output)
