from unittest import TestCase

from ..elements import (
    Intent,
    Entity,
    Datum,
)
from ..exceptions import (
    EntityOverlapping,
    EntityPositionError,
)


class ElementIntentTestCase(TestCase):

    def setUp(self):
        self.intent_label = 1
        self.intent = Intent(self.intent_label)

    def test_init(self):
        self.assertEqual(self.intent.label, self.intent_label)

    def test_representation(self):
        self.assertEqual(f"<Intent {self.intent_label}>", self.intent.__repr__())


class ElementEntityTestCase(TestCase):

    def test_no_replacements(self):
        ent = Entity(
            label=1,
            value='紐約',
            start=1,
            end=3,
        )
        self.assertTrue(ent.no_replacements())
        self.assertEqual("<Entity 1: 紐約 at 1 - 3, with replacements: >", ent.__repr__())

    def test_has_replacements(self):
        ent = Entity(
            label=1,
            value='紐約',
            start=1,
            end=3,
            replacements=['台北'],
        )
        self.assertFalse(ent.no_replacements())
        self.assertEqual("<Entity 1: 紐約 at 1 - 3, with replacements: 台北>", ent.__repr__())

    def test_from_dict(self):
        label = 1
        start = 1
        end = 3
        replacements = ['斯堪地那維亞', 'KIX']
        utterance = '去紐約的機票'
        entity = {
            'label': label,
            'start': start,
            'end': end,
            'replacements': replacements,
        }
        ent = Entity.from_dict(entity, utterance)
        self.assertIsInstance(ent, Entity)
        self.assertEqual(ent.value, '紐約')
        self.assertEqual(ent.label, 1)
        self.assertEqual(ent.start, start)
        self.assertEqual(ent.end, end)
        self.assertEqual(ent.replacements, set(replacements))
        self.assertIn(
            ent.__repr__(),
            [
                "<Entity 1: 紐約 at 1 - 3, with replacements: 斯堪地那維亞, KIX>",
                "<Entity 1: 紐約 at 1 - 3, with replacements: KIX, 斯堪地那維亞>",
            ],
        )

    def test_from_dict_no_replacements(self):
        label = 1
        start = 1
        end = 3
        utterance = '去紐約的機票'
        entity = {
            'label': label,
            'start': start,
            'end': end,
        }
        ent = Entity.from_dict(entity, utterance)
        self.assertIsInstance(ent, Entity)
        self.assertEqual(ent.value, '紐約')
        self.assertEqual(ent.label, 1)
        self.assertEqual(ent.start, start)
        self.assertEqual(ent.end, end)
        self.assertEqual(ent.replacements, set([]))
        self.assertEqual("<Entity 1: 紐約 at 1 - 3, with replacements: >", ent.__repr__())

    def test_to_dict(self):
        label = 1
        start = 1
        end = 3
        replacements = ['斯堪地那維亞', 'KIX']
        entity = {
            'label': label,
            'start': start,
            'end': end,
            'replacements': replacements,
        }
        ent = Entity(
            label=label,
            value='紐約',
            start=start,
            end=end,
            replacements=replacements,
        )
        ent_tx = ent.to_dict()
        self.assertEqual(ent_tx['label'], entity['label'])
        self.assertEqual(ent_tx['start'], entity['start'])
        self.assertEqual(ent_tx['end'], entity['end'])
        self.assertEqual(set(ent_tx['replacements']),
                         set(entity['replacements']))

    def test_to_dict_no_replacement(self):
        label = 1
        start = 1
        end = 3
        entity = {
            'label': label,
            'start': start,
            'end': end,
        }
        ent = Entity(
            label=label,
            value='紐約',
            start=start,
            end=end,
        )
        ent_tx = ent.to_dict()
        self.assertEqual(ent_tx['label'], entity['label'])
        self.assertEqual(ent_tx['start'], entity['start'])
        self.assertEqual(ent_tx['end'], entity['end'])
        self.assertNotIn('replacements', ent_tx)

    def test_equal(self):
        ent1 = Entity(
            label=1,
            value='紐約',
            start=1,
            end=3,
            replacements=['台北'],
        )
        ent2 = Entity(
            label=1,
            value='紐約',
            start=1,
            end=3,
            replacements=['台北'],
        )
        self.assertEqual(ent1, ent2)

    def test_not_equal(self):
        ent = Entity(
            label=1,
            value='紐約',
            start=1,
            end=2,
            replacements=['台北'],
        )
        ent_diff_label = Entity(
            label=2,
            value='紐約',
            start=1,
            end=2,
            replacements=['台北'],
        )
        ent_diff_value = Entity(
            label=1,
            value='新加坡',
            start=1,
            end=2,
            replacements=['台北'],
        )
        ent_diff_start = Entity(
            label=1,
            value='紐約',
            start=0,
            end=2,
            replacements=['台北'],
        )
        ent_diff_end = Entity(
            label=1,
            value='紐約',
            start=1,
            end=3,
            replacements=['台北'],
        )
        ent_diff_replacements = Entity(
            label=1,
            value='紐約',
            start=1,
            end=2,
            replacements=['台北', 'KIX'],
        )
        self.assertNotEqual(ent, ent_diff_label)
        self.assertNotEqual(ent, ent_diff_value)
        self.assertNotEqual(ent, ent_diff_start)
        self.assertNotEqual(ent, ent_diff_end)
        self.assertNotEqual(ent, ent_diff_replacements)

    def test_raise_error_if_compare_different_type(self):
        ent = Entity(
            label=1,
            value='紐約',
            start=1,
            end=2,
            replacements=['台北'],
        )
        ent_diff_type = object()
        with self.assertRaises(TypeError):
            ent == ent_diff_type


class ElementDatumTestCase(TestCase):

    def test_raise_entity_position_error_if_entity_position_wrong(self):
        with self.subTest(case='wrong end'):
            with self.assertRaises(EntityPositionError):
                Datum(
                    utterance='去紐約的機票',
                    intents=[Intent(0)],
                    entities=[
                        Entity(label=1, value='紐約', start=1, end=2),
                    ],
                )
        with self.subTest(case='wrong start'):
            with self.assertRaises(EntityPositionError):
                Datum(
                    utterance='去紐約的機票',
                    intents=[Intent(0)],
                    entities=[
                        Entity(label=1, value='紐約', start=0, end=3),
                    ],
                )
        with self.subTest(case='wrong value'):
            with self.assertRaises(EntityPositionError):
                Datum(
                    utterance='去紐曰的機票',
                    intents=[Intent(0)],
                    entities=[
                        Entity(label=1, value='紐約', start=1, end=3),
                    ],
                )

    def test_raise_entity_overlap_if_entity_overlaps(self):
        with self.assertRaises(EntityOverlapping):
            Datum(
                utterance='我想吃麥當勞快樂兒童餐',
                intents=[Intent(0)],
                entities=[
                    Entity(label=0, value='快樂', start=6, end=8),
                    Entity(label=1, value='快樂兒童餐', start=6, end=11),
                ],
            )

    def test_entities_correct_order_in_datum(self):
        utterance = '我想訂明天從紐約飛到新加坡的機票'
        entities = [
            Entity(label=0, value='新加坡', start=10,
                   end=13, replacements=['斯堪地那維亞', 'KIX']),
            Entity(label=1, value='明天', start=3,
                   end=5, replacements=['下禮拜二']),
            Entity(label=2, value='紐約', start=6, end=8),
        ]
        intents = [
            Intent(1),
        ]
        datum = Datum(
            utterance=utterance,
            intents=intents,
            entities=entities,
        )

        expected_entities = [
            Entity(label=1, value='明天', start=3,
                   end=5, replacements=['下禮拜二']),
            Entity(label=2, value='紐約', start=6, end=8),
            Entity(label=0, value='新加坡', start=10,
                   end=13, replacements=['斯堪地那維亞', 'KIX']),
        ]
        for result_entity, expected_entity in zip(datum.entities, expected_entities):
            self.assertEqual(result_entity.label, expected_entity.label)
            self.assertEqual(result_entity.value, expected_entity.value)
            self.assertEqual(result_entity.start, expected_entity.start)
            self.assertEqual(result_entity.end, expected_entity.end)

    def test_has_entities(self):
        datum = Datum(
            utterance='去紐約的機票',
            intents=[Intent(0)],
            entities=[
                Entity(label=1, value='紐約', start=1, end=3),
            ],
        )
        self.assertTrue(datum.has_entities())

    def test_has_no_entities(self):
        datum = Datum(
            utterance='去紐約的機票',
            intents=[Intent(0)],
            entities=[],
        )
        self.assertFalse(datum.has_entities())

    def test_has_intents(self):
        datum = Datum(
            utterance='去紐約的機票',
            intents=[Intent(0)],
            entities=[
                Entity(label=1, value='紐約', start=1, end=3),
            ],
        )
        self.assertTrue(datum.has_intents())

    def test_has_no_intents(self):
        datum = Datum(
            utterance='去紐約的機票',
            intents=None,
            entities=[
                Entity(label=1, value='紐約', start=1, end=3),
            ],
        )
        self.assertFalse(datum.has_intents())

    def test_same_utterance(self):
        utterance = '我想訂明天從紐約飛到新加坡的機票'
        entities = [
            Entity(label=0, value='新加坡', start=10,
                   end=13, replacements=['斯堪地那維亞', 'KIX']),
            Entity(label=1, value='明天', start=3,
                   end=5, replacements=['下禮拜二']),
            Entity(label=2, value='紐約', start=6, end=8),
        ]
        intents = [
            Intent(1),
        ]
        datum = Datum(
            utterance=utterance,
            intents=intents,
            entities=entities,
        )
        datum2 = Datum(
            utterance=utterance,
        )
        self.assertTrue(datum.has_same_utterance_as(datum2))

    def test_same_intents(self):
        utterance = '我想訂明天從紐約飛到新加坡的機票'
        utterance2 = '我想訂機票'
        entities = [
            Entity(label=0, value='新加坡', start=10,
                   end=13, replacements=['斯堪地那維亞', 'KIX']),
            Entity(label=1, value='明天', start=3,
                   end=5, replacements=['下禮拜二']),
            Entity(label=2, value='紐約', start=6, end=8),
        ]
        intents = [
            Intent(1),
        ]
        intents2 = [
            Intent(1),
        ]
        datum = Datum(
            utterance=utterance,
            intents=intents,
            entities=entities,
        )
        datum2 = Datum(
            utterance=utterance2,
            intents=intents2,
        )
        self.assertTrue(datum.has_same_intents_as(datum2))

    def test_same_entities(self):
        utterance = '我想訂明天從紐約飛到新加坡的機票'
        utterance2 = '我想查明天從紐約飛往新加坡的機票'
        entities = [
            Entity(label=0, value='新加坡', start=10,
                   end=13, replacements=['斯堪地那維亞', 'KIX']),
            Entity(label=1, value='明天', start=3,
                   end=5, replacements=['下禮拜二']),
            Entity(label=2, value='紐約', start=6, end=8),
        ]
        entities2 = [
            Entity(label=0, value='新加坡', start=10,
                   end=13, replacements=['斯堪地那維亞', 'KIX']),
            Entity(label=1, value='明天', start=3,
                   end=5, replacements=['下禮拜二']),
            Entity(label=2, value='紐約', start=6, end=8),
        ]
        intents = [
            Intent(1),
        ]
        intents2 = [
            Intent(0),
        ]
        datum = Datum(
            utterance=utterance,
            intents=intents,
            entities=entities,
        )
        datum2 = Datum(
            utterance=utterance2,
            intents=intents2,
            entities=entities2,
        )
        self.assertTrue(datum.has_same_entities_as(datum2))
