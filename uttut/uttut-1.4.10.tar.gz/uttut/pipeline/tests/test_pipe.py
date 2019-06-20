import pytest

from uttut.elements import Datum, Intent, Entity
from ..pipe import Pipe


@pytest.fixture(scope='module')
def fake_pipe():
    p_custom = Pipe()
    p_custom.add('Str2Str', {'1': 1}, checkpoint='1')
    p_custom.add('Str2Lst', {})
    p_custom.add('Lst2Lst', {}, checkpoint='2')
    return p_custom


@pytest.fixture(scope='module')
def dummy_datum():
    return Datum(
        utterance='123',
        intents=[Intent(1)],
        entities=[
            Entity(label=1, start=0, end=1, value='1'),
            Entity(label=2, start=1, end=2, value='2'),
            Entity(label=3, start=2, end=3, value='3'),
        ],
    )


def test_pipe_raise_invalid_io_type():
    p = Pipe()
    p.add('Lst2Lst')
    with pytest.raises(TypeError):
        p.add('Str2Str')


def test_pipe_raise_duplicated_checkpoints():
    p = Pipe()
    p.add('Str2Str', checkpoint='1')
    with pytest.raises(KeyError):
        p.add('Str2Lst', checkpoint='1')


def test_pipe_can_have_duplicated_ops():
    p = Pipe()
    p.add('Str2Str', checkpoint='1')
    p.add('Str2Str', checkpoint='2')


def test_transform(fake_pipe, dummy_datum):
    output = fake_pipe.transform(dummy_datum)
    output_seq, intent_labels, entity_labels, label_aligner, intermediate = output

    assert output_seq == ['1', '2', '3']
    assert intent_labels == [1]
    assert entity_labels == [1, 2, 3]

    # intermediate
    assert '123' == intermediate.get_from_checkpoint('1')
    assert ['1', '2', '3'] == intermediate.get_from_checkpoint('2')
    assert ['123', '123', ['1', '2', '3'], ['1', '2', '3']] == intermediate[:]

    with pytest.raises(KeyError):
        intermediate.get_from_checkpoint('薄餡亂入')

    # realign labels
    output = label_aligner.inverse_transform(entity_labels)
    assert output == [1, 2, 3]


def test_serialize(fake_pipe):
    serialized_str = fake_pipe.serialize()
    o_pipe = Pipe.deserialize(serialized_str)
    assert fake_pipe == o_pipe


def test_deserialize_from_old_format(get_data_path):
    path = get_data_path('zh_char_pipe_100_old_format.json')
    with open(path, 'r') as f_in:
        Pipe.deserialize(f_in.read())


def test_add(fake_pipe):
    p2 = Pipe()
    p2.add('Lst2Str', checkpoint='3')
    concat_pipe = fake_pipe + p2
    assert concat_pipe.steps == fake_pipe.steps + p2.steps
    assert len(concat_pipe.checkpoints) == len(fake_pipe.checkpoints) + len(p2.checkpoints)
    assert concat_pipe.input_type == fake_pipe.input_type
    assert concat_pipe.output_type == p2.output_type


def test_raise_invalid_add(fake_pipe):
    p2 = Pipe()
    p2.add('Str2Str')
    with pytest.raises(TypeError):
        fake_pipe + p2  # invalid io type

    p3 = Pipe()
    p3.add('Lst2Str', checkpoint='1')
    with pytest.raises(KeyError):
        fake_pipe + p3  # duplicated checkpoints


def test_len(fake_pipe):
    assert len(fake_pipe) == len(fake_pipe.steps)


def test_getitem(fake_pipe):
    sub_pipe = fake_pipe[1: -1]
    assert sub_pipe.steps == fake_pipe.steps[1: -1]
    assert sub_pipe.checkpoints == {'2': 2}


def test_summary(fake_pipe):
    fake_pipe.summary()
