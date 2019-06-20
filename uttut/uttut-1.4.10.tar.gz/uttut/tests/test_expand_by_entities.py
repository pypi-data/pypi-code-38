from unittest import TestCase
from unittest.mock import patch, Mock, call

from ..expand_by_entities import (
    expand_by_entities,
    _aggregate_entities,
)
from ..elements import (
    Datum,
    Entity,
    Intent,
)


class ExpandByEntitiesTestCase(TestCase):

    def setUp(self):
        self.utterance = '我想訂明天從紐約飛到新加坡的機票'
        self.entities = [
            Entity(label=1, value='明天', start=3, end=5, replacements=['下禮拜二']),
            Entity(label=2, value='紐約', start=6, end=8),
            Entity(label=3, value='新加坡', start=10, end=13, replacements=['斯堪地那維亞', 'KIX']),
        ]
        self.intents = [
            Intent(label=0),
        ]
        self.datum = Datum(
            utterance=self.utterance,
            intents=self.intents,
            entities=self.entities,
        )

        self.expected_utterances = [
            '我想訂明天從紐約飛到新加坡的機票',
            '我想訂明天從紐約飛到斯堪地那維亞的機票',
            '我想訂明天從紐約飛到KIX的機票',
            '我想訂下禮拜二從紐約飛到新加坡的機票',
            '我想訂下禮拜二從紐約飛到斯堪地那維亞的機票',
            '我想訂下禮拜二從紐約飛到KIX的機票',
        ]
        self.expected_entity_lists = [
            [
                Entity(label=1, value='明天', start=3, end=5),
                Entity(label=2, value='紐約', start=6, end=8),
                Entity(label=3, value='新加坡', start=10, end=13),
            ],
            [
                Entity(label=1, value='明天', start=3, end=5),
                Entity(label=2, value='紐約', start=6, end=8),
                Entity(label=3, value='斯堪地那維亞', start=10, end=16),
            ],
            [
                Entity(label=1, value='明天', start=3, end=5),
                Entity(label=2, value='紐約', start=6, end=8),
                Entity(label=3, value='KIX', start=10, end=13),
            ],
            [
                Entity(label=1, value='下禮拜二', start=3, end=7),
                Entity(label=2, value='紐約', start=8, end=10),
                Entity(label=3, value='新加坡', start=12, end=15),
            ],
            [
                Entity(label=1, value='下禮拜二', start=3, end=7),
                Entity(label=2, value='紐約', start=8, end=10),
                Entity(label=3, value='斯堪地那維亞', start=12, end=18),
            ],
            [
                Entity(label=1, value='下禮拜二', start=3, end=7),
                Entity(label=2, value='紐約', start=8, end=10),
                Entity(label=3, value='KIX', start=12, end=15),
            ],
        ]
        self.expected_intents = [
            [Intent(label=0)],
            [Intent(label=0)],
            [Intent(label=0)],
            [Intent(label=0)],
            [Intent(label=0)],
            [Intent(label=0)],
        ]
        self.expected_data = []
        self.expected_data_without_replacement = []
        for utt, ents, ints in zip(
                self.expected_utterances,
                self.expected_entity_lists,
                self.expected_intents,
            ):
            self.expected_data.append(Datum(
                utterance=utt,
                entities=ents,
                intents=ints,
            ))

    def test_include_original_value(self):
        result = expand_by_entities(
            self.datum,
            include_orig=True,
        )

        # correct expand numbers
        self.assertEqual(6, len(result))
        for idx, datum in enumerate(result):
            with self.subTest(datum_idx=idx):
                self.assertIn(datum, self.expected_data)

    def test_exclude_original_value(self):
        result = expand_by_entities(
            self.datum,
            include_orig=False,
        )
        # correct expand numbers
        self.assertEqual(2, len(result))
        for idx, datum in enumerate(result):
            with self.subTest(datum_idx=idx):
                self.assertIn(datum, self.expected_data[4:])

    def test_datum_without_entities(self):
        datum_wo_entities = Datum(
            utterance='薄餡亂入',
            intents=[Intent(label=0)],
        )
        for include_orig in [True, False]:
            with self.subTest(include_orig_or_not=include_orig):
                result = expand_by_entities(datum_wo_entities, include_orig)
                self.assertEqual([datum_wo_entities], result)

    @patch('uttut.expand_by_entities.partition_by_entities', return_value=([[]], []))
    def test_expand_by_entities_call_partition_correctly(self, patch_partition):
        expand_by_entities(
            self.datum,
            include_orig=True,
        )
        patch_partition.assert_called_once_with(self.datum, True)

    @patch('uttut.expand_by_entities.partition_by_entities', return_value=([[]], []))
    def test_expand_by_entities_call_partition_correctly_false(self, patch_partition):
        expand_by_entities(
            self.datum,
            include_orig=False,
        )
        patch_partition.assert_called_once_with(self.datum, False)

    fake_parts = [['a', 'b'], ['c']]
    fake_entity_labels = [1, None]

    @patch(
        'uttut.expand_by_entities.partition_by_entities',
        return_value=(fake_parts, fake_entity_labels),
    )
    @patch('uttut.expand_by_entities.get_kth_combination', return_value=['a', 'c'])
    def test_expand_by_entities_correctly_use_sampling_method(self, patch_get_k, _):
        mock_sampling_method = Mock(return_value=[0, 1])

        expand_by_entities(
            self.datum,
            sampling_method=mock_sampling_method,
            include_orig=True,
        )

        mock_sampling_method.assert_called_once_with(2)
        patch_get_k.assert_has_calls([
            call(self.fake_parts, 0),
            call(self.fake_parts, 1),
        ])

    def test__aggregate_entities(self):
        segments = ['我想喝', '珍奶', '半糖']
        entity_names = [None, 1, 2]

        expected_entities = [
            Entity(label=1, value='珍奶', start=3, end=5),
            Entity(label=2, value='半糖', start=5, end=7),
        ]

        actual_entities = _aggregate_entities(segments, entity_names)
        self.assertEqual(expected_entities, actual_entities)
