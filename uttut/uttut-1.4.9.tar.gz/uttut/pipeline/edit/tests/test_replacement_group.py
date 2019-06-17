import pytest

from ..replacement import ReplacementGroup, Replacement


@pytest.mark.filterwarnings("ignore")
def test_correctly_init():
    replacement_group = ReplacementGroup()
    assert replacement_group.is_empty() is True
    assert len(replacement_group) == 0


@pytest.mark.parametrize(
    "objs",
    [
        pytest.param([(0, 0, 'a'), (0, 2, 'b')], id='str-replacement'),
        pytest.param([(0, 0, 'a', 'ohoh'), (0, 2, 'b', 'ohoh1')],
                     id='str-replacement with annotation'),
        pytest.param([(0, 0, ['a']), (0, 2, ['b'])], id='list-replacement'),
        pytest.param([(0, 0, ['a'], 'ohoh'), (0, 2, ['b'], 'ohoh1')],
                     id='list-replacement with annotation'),
    ],
)
def test_add_all(objs):
    replacement_group = ReplacementGroup.add_all(objs)
    assert len(replacement_group) == len(objs)
    assert [Replacement(*obj) for obj in objs] == replacement_group[:]


def test_add_all_empty():
    replacement_group = ReplacementGroup.add_all([])
    assert replacement_group.is_empty() is True


def test_not_done_warning():
    replacement_group = ReplacementGroup()
    with pytest.warns(UserWarning, match='ReplacementGroup needs validation, please call `done`.'):
        len(replacement_group)


def test_not_done_error():
    replacement_group = ReplacementGroup()
    replacement_group.add(1, 3, 'abc')
    with pytest.raises(RuntimeError, match='Please call `done` first.'):
        replacement_group[0]


@pytest.mark.parametrize(
    "obj,error_type",
    [
        pytest.param([(0,)], TypeError, id='lack of elements'),
        pytest.param([(0, 0, 'a', 'a', 'a')], TypeError, id='has redundant elements'),
        pytest.param([(0, 1, 'a'), (0, 2, ['b']), (3, 5, 10000)],
                     TypeError, id='mixed replacements'),
    ],
)
def test_add_fails(obj, error_type):
    with pytest.raises(error_type):
        ReplacementGroup.add_all(obj)


@pytest.mark.parametrize(
    "input1,input2",
    [
        pytest.param([], [], id='empty'),
        pytest.param([(0, 0, 'a'), (1, 2, 'b')], [(0, 0, 'a'), (1, 2, 'b')],
                     id='str-replacement'),
        pytest.param([(0, 0, ['a']), (1, 2, ['b'])], [(0, 0, ['a']), (1, 2, ['b'])],
                     id='list-replacement'),
    ],
)
def test_equal(input1, input2):
    group1 = ReplacementGroup.add_all(input1)
    group2 = ReplacementGroup.add_all(input2)
    assert group1 == group2


@pytest.mark.parametrize(
    "input1,input2",
    [
        pytest.param([(0, 0, 'a')], [(0, 0, 'a'), (1, 2, 'b')],
                     id='different length'),
        pytest.param([(0, 0, 'a'), (1, 2, 'b')], [(0, 0, 'a'), (1, 3, 'b')],
                     id='different element'),
        pytest.param([(0, 0, 'a'), (1, 2, 'b')], [(0, 0, ['a']), (1, 3, ['b'])],
                     id='different type of replacement'),
    ],
)
def test_not_equal(input1, input2):
    group1 = ReplacementGroup.add_all(input1)
    group2 = ReplacementGroup.add_all(input2)
    assert group1 != group2


def test_different_type():
    input_lst = [(0, 0, 'a')]
    assert input_lst != ReplacementGroup.add_all(input_lst)


@pytest.mark.parametrize(
    "objs,expected_objs",
    [
        pytest.param([(1, 2, 'b'), (0, 1, 'a')], [Replacement(0, 1, 'a'), Replacement(1, 2, 'b')]),
    ],
)
def test_need_sorted(objs, expected_objs):
    obj_group = ReplacementGroup.add_all(objs)
    assert expected_objs == obj_group[:]


@pytest.mark.parametrize(
    "objs",
    [
        pytest.param([(1, 10, 'b'), (2, 15, 'a')], id='intersect'),
        pytest.param([(1, 10, 'b'), (2, 8, 'a')], id='include'),
    ],
)
def test_validate_disjoint(objs):
    with pytest.raises(ValueError):
        ReplacementGroup.add_all(objs)


@pytest.mark.parametrize(
    "representation,input_lst",
    [
        pytest.param('ReplacementGroup has 1 elements', [(0, 0, 'a')], id='str-replacement'),
        pytest.param('ReplacementGroup has 0 elements', [], id='empty'),
    ],
)
def test_representation(representation, input_lst):
    group = ReplacementGroup.add_all(input_lst)
    assert representation == repr(group)
