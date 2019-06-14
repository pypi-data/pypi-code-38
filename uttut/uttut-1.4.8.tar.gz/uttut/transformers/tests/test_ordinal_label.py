from unittest.mock import Mock, call

import pytest

from uttut import NOT_ENTITY
from uttut.elements import Datum, Intent, Entity
from ..ordinal_label import OrdinalLabel


TRANSFORMATION_PAIRS = [
    (
        {
            'utterance': '你好',
            'intent': {'names': ['HI']},
        },
        Datum(utterance='你好', intents=[Intent(0)]),
    ),
    (
        {
            "utterance": "我想喝珍奶半糖",
            "intent": {
                "names": ["ORDER"],
            },
            "entities": [
                {
                    "name": "ITEM",
                    "start": 3,
                    "end": 5,
                    "replacements": ["拿鐵", "多多綠", "紅茶"],
                },
                {
                    "name": "SUGAR",
                    "start": 5,
                    "end": 7,
                    "replacements": ["無糖", "全糖"],
                },
            ],
        },
        Datum(
            utterance='我想喝珍奶半糖',
            intents=[Intent(2)],
            entities=[
                Entity(1, '珍奶', 3, 5, ["拿鐵", "多多綠", "紅茶"]),
                Entity(2, '半糖', 5, 7, ["無糖", "全糖"]),
            ],
        ),
    ),
]


@pytest.fixture(scope='function')
def tx():
    intent2index = {'HI': 0, 'BYE': 1, 'ORDER': 2}
    entity2index = {'ITEM': 1, 'SUGAR': 2}
    not_entity_index = 0
    tx = OrdinalLabel(intent2index, entity2index, not_entity_index)
    return tx


@pytest.yield_fixture
def mocked_OrdinalLabel():
    orig_checker = OrdinalLabel.is_valid_mapping
    OrdinalLabel.is_valid_mapping = Mock(return_value=True)
    yield OrdinalLabel
    OrdinalLabel.is_valid_mapping = orig_checker


def test_ordinal_label_init(mocked_OrdinalLabel):
    intent2index = {'HI': 0, 'BYE': 1, 'ORDER': 2}
    entity2index = {'DRINK': 0, 'SIZE': 1}
    not_entity_index = 2
    tx = mocked_OrdinalLabel(intent2index, entity2index, not_entity_index)
    assert tx._intent2index == intent2index
    assert tx._entity2index == entity2index
    assert tx._not_entity_index == not_entity_index

    assert tx.not_entity_index == not_entity_index

    actual_calls = mocked_OrdinalLabel.is_valid_mapping.call_args_list
    expected_calls = [
        call(intent2index),
        call({**entity2index, NOT_ENTITY: 2}),
    ]
    assert expected_calls == actual_calls


def test_ordinal_label_init_raise_if_intent2index_not_valid():
    # setup
    orig_checker = OrdinalLabel.is_valid_mapping
    OrdinalLabel.is_valid_mapping = Mock(side_effect=[False, True])

    intent2index = {}
    entity2index = {}
    with pytest.raises(ValueError):
        OrdinalLabel(intent2index, entity2index)

    # tear down
    OrdinalLabel.is_valid_mapping = orig_checker


def test_ordinal_label_init_raise_if_entity2index_not_valid():
    # setup
    orig_checker = OrdinalLabel.is_valid_mapping
    OrdinalLabel.is_valid_mapping = Mock(side_effect=[True, False])

    intent2index = {}
    entity2index = {}
    with pytest.raises(ValueError):
        OrdinalLabel(intent2index, entity2index)

    # tear down
    OrdinalLabel.is_valid_mapping = orig_checker


def test_ordinal_label_is_valid_mapping():
    correct_mapping = {'HI': 0, 'BYE': 1, 'ORDER': 2}
    duplicate_mapping = {'HI': 0, 'BYE': 1, 'ORDER': 1}
    non_ordinal_mapping = {'HI': 0, 'BYE': 1, 'ORDER': 3}
    mapping_with_negative = {'HI': -1, 'BYE': 0, 'ORDER': 1}
    assert OrdinalLabel.is_valid_mapping(correct_mapping)
    assert not OrdinalLabel.is_valid_mapping(duplicate_mapping)
    assert not OrdinalLabel.is_valid_mapping(non_ordinal_mapping)
    assert not OrdinalLabel.is_valid_mapping(mapping_with_negative)


@pytest.mark.parametrize('expected, datum', TRANSFORMATION_PAIRS)
def test_ordinal_label_humanize(expected, datum, tx):
    actual = tx.humanize(datum)
    assert set(actual.keys()) == set(expected.keys())
    assert actual['utterance'] == expected['utterance']
    assert set(actual['intent']['names']) == set(expected['intent']['names'])
    assert len(actual.get('entities', [])) == len(expected.get('entities', []))

    if len(actual.get('entities', [])) > 0:
        for actual_entity, expected_entity in zip(actual['entities'], expected['entities']):
            assert actual_entity['name'] == expected_entity['name']
            assert actual_entity['start'] == expected_entity['start']
            assert actual_entity['end'] == expected_entity['end']
            actual_replacements = set(actual_entity.get('replacements', []))
            expected_replacements = set(expected_entity.get('replacements', []))
            assert actual_replacements == expected_replacements


@pytest.mark.parametrize('raw_dict, datum', TRANSFORMATION_PAIRS)
def test_ordinal_label_machanize(raw_dict, datum, tx):
    assert tx.machanize(raw_dict) == datum


def test_ordinal_label_serialization():
    intent2index = {'HI': 0, 'BYE': 1, 'ORDER': 2}
    entity2index = {'DRINK': 1, 'SIZE': 2}
    tx = OrdinalLabel(intent2index, entity2index)

    serialized = tx.serialize()
    loaded_tx = OrdinalLabel.deserialize(serialized)

    assert tx._intent2index == loaded_tx._intent2index
    assert tx._entity2index == loaded_tx._entity2index


@pytest.fixture(scope='function')
def raw_data():
    return {
        "data": [
            {
                "utterance": "你好",
                "intent": {
                    "names": ["GREETINGS"],
                },
            },
            {
                "utterance": "我想喝珍奶半糖",
                "intent": {
                    "names": ["ORDER"],
                },
                "entities": [
                    {
                        "name": "ITEM",
                        "start": 3,
                        "end": 5,
                        "replacements": ["拿鐵", "多多綠", "紅茶"],
                    },
                    {
                        "name": "SUGAR",
                        "start": 5,
                        "end": 7,
                        "replacements": ["無糖", "全糖"],
                    },
                ],
            },
        ],
    }


def test_ordinal_from_raw_dictionary(raw_data):
    tx = OrdinalLabel.from_raw_dictionary(raw_data)
    # indexes are based on the appearance order
    assert tx._intent2index == {"GREETINGS": 0, "ORDER": 1}
    assert tx._entity2index == {"ITEM": 1, "SUGAR": 2}


def test_ordinal_from_raw_dictionary_with_custom_not_entity_index(raw_data):
    tx = OrdinalLabel.from_raw_dictionary(raw_data, not_entity_index=1)
    # indexes are based on the appearance order
    assert tx._intent2index == {"GREETINGS": 0, "ORDER": 1}
    assert tx._entity2index == {"ITEM": 0, "SUGAR": 2}


def test_ordinal_from_raw_dictionary_with_custom_not_entity_index_2(raw_data):
    tx = OrdinalLabel.from_raw_dictionary(raw_data, not_entity_index=2)
    # indexes are based on the appearance order
    assert tx._intent2index == {"GREETINGS": 0, "ORDER": 1}
    assert tx._entity2index == {"ITEM": 0, "SUGAR": 1}


@pytest.mark.parametrize('wrong_entity_index', [0., 1., 100., 0.1, '0', '0.1'])
def test_ordinal_from_raw_dictionary_raise_with_wrong_type(wrong_entity_index):
    raw_data = {'data': []}
    with pytest.raises(TypeError):
        OrdinalLabel.from_raw_dictionary(raw_data, not_entity_index=wrong_entity_index)
