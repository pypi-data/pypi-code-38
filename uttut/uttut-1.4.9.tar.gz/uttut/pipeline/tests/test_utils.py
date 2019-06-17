import pytest

from ..utils import unpack_datum, pack_to_datum
from uttut.elements import Datum, Intent, Entity
from uttut import ENTITY_LABEL

not_entity = ENTITY_LABEL['NOT_ENTITY']


def test_unpack_datum():
    utterance = '我想訂明天從紐約飛到新加坡的機票'
    entities = [
        Entity(label=1, value='新加坡', start=10,
               end=13, replacements=['斯堪地那維亞', 'KIX']),
        Entity(label=2, value='明天', start=3,
               end=5, replacements=['下禮拜二']),
        Entity(label=3, value='紐約', start=6, end=8),
    ]
    intents = [Intent(1)]
    datum = Datum(
        utterance=utterance,
        intents=intents,
        entities=entities,
    )
    output_utt, output_intent, output_entity = unpack_datum(datum)

    assert utterance == output_utt
    assert [1] == output_intent
    assert [0, 0, 0, 2, 2, 0, 3, 3, 0, 0, 1, 1, 1, 0, 0, 0] == output_entity


@pytest.mark.parametrize(
    "input_tuple,expected_datum",
    [
        pytest.param(
            ("abb", [1, 2], [1, 2, 2]),
            Datum(
                "abb",
                [Intent(1), Intent(2)],
                [Entity(1, "a", 0, 1), Entity(2, "bb", 1, 3)],
            ),
            id='all entities',
        ),
        pytest.param(
            ("acbb", [1, 2], [1, not_entity, 2, 2]),
            Datum(
                "acbb",
                [Intent(1), Intent(2)],
                [Entity(1, "a", 0, 1), Entity(2, "bb", 2, 4)],
            ),
            id='not entity in the middle',
        ),
        pytest.param(
            (" acbb", [1, 2], [not_entity, 1, not_entity, 2, 2]),
            Datum(
                " acbb",
                [Intent(1), Intent(2)],
                [Entity(1, "a", 1, 2), Entity(2, "bb", 3, 5)],
            ),
            id='not entity in head',
        ),
        pytest.param(
            (" acbbo", [1, 2], [not_entity, 1, not_entity, 2, 2, not_entity]),
            Datum(
                " acbbo",
                [Intent(1), Intent(2)],
                [Entity(1, "a", 1, 2), Entity(2, "bb", 3, 5)],
            ),
            id='not entity in tail',
        ),
        pytest.param(
            ("abb", [1, 2, 2, 1, 1, 1], [1, 2, 2]),
            Datum(
                "abb",
                [Intent(1), Intent(2)],
                [Entity(1, "a", 0, 1), Entity(2, "bb", 1, 3)],
            ),
            id='duplicated intent labels',
        ),
        pytest.param(
            ("abc", [1, 2], [1, 2, 3]),
            Datum(
                "abc",
                [Intent(1), Intent(2)],
                [Entity(1, "a", 0, 1), Entity(2, "b", 1, 2), Entity(3, "c", 2, 3)],
            ),
            id='char-level all different',
        ),
    ],
)
def test_pack_to_datum(input_tuple, expected_datum):
    output = pack_to_datum(*input_tuple)
    assert expected_datum == output


def test_pack_to_datum_fail():
    with pytest.raises(ValueError):
        pack_to_datum('abb', [1, 2], [1, 3])
