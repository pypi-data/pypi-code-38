import pytest

from ..span import Span, SpanGroup


@pytest.mark.filterwarnings("ignore")
def test_correctly_init():
    span_group = SpanGroup()
    assert span_group.is_empty() is True
    assert len(span_group) == 0


@pytest.mark.parametrize(
    "spans",
    [
        pytest.param([(0, 1), (3, 5)], id='not contiguous'),
        pytest.param([(1, 3), (3, 5)], id='not start from 0'),
    ],
)
def test_span_group_should_be_contiguous(spans):
    with pytest.raises(ValueError):
        SpanGroup.add_all(spans)


def test_add_all():
    objs = [(0, 0), (0, 2)]
    span_group = SpanGroup.add_all(objs)
    assert len(span_group) == len(objs)
    assert [Span(*obj) for obj in objs] == span_group[:]


def test_add_all_empty():
    span_group = SpanGroup.add_all([])
    assert span_group.is_empty() is True


def test_not_done_warning():
    span_group = SpanGroup()
    with pytest.warns(UserWarning, match='SpanGroup needs validation, please call `done`.'):
        len(span_group)


def test_not_done_error():
    span_group = SpanGroup()
    span_group.add(1, 3)
    with pytest.raises(RuntimeError, match='Please call `done` first.'):
        span_group[0]


@pytest.mark.parametrize(
    "obj,error_type",
    [
        pytest.param([(0,)], ValueError, id='lack of elements'),
        pytest.param([(0, 0, 3)], ValueError, id='has redundant elements'),
    ],
)
def test_add_fails(obj, error_type):
    with pytest.raises(error_type):
        SpanGroup.add_all(obj)


@pytest.mark.parametrize(
    "group1,group2",
    [
        pytest.param(SpanGroup.add_all([]), SpanGroup.add_all([]), id='empty'),
        pytest.param(SpanGroup.add_all([(0, 0), (0, 2)]),
                     SpanGroup.add_all([(0, 0), (0, 2)]), id='span'),
    ],
)
def test_equal(group1, group2):
    assert group1 == group2


@pytest.mark.parametrize(
    "group1,group2",
    [
        pytest.param(SpanGroup.add_all([(0, 0)]), [(0, 0)], id='different type'),
        pytest.param(SpanGroup.add_all([(0, 0)]), SpanGroup.add_all([(0, 0), (0, 2)]),
                     id='different length'),
        pytest.param(SpanGroup.add_all([(0, 0), (0, 2)]), SpanGroup.add_all([(0, 0), (0, 3)]),
                     id='different element'),
    ],
)
def test_not_equal(group1, group2):
    assert group1 != group2


@pytest.mark.parametrize(
    "objs,expected_objs",
    [
        pytest.param([(1, 2), (0, 1)], [Span(0, 1), Span(1, 2)]),
    ],
)
def test_need_sorted(objs, expected_objs):
    obj_group = SpanGroup.add_all(objs)
    assert expected_objs == obj_group[:]


@pytest.mark.parametrize(
    "objs",
    [
        pytest.param([(1, 10), (2, 15)], id='intersect'),
        pytest.param([(1, 10), (2, 8)], id='include'),
    ],
)
def test_validate_disjoint(objs):
    with pytest.raises(ValueError):
        SpanGroup.add_all(objs)


@pytest.mark.parametrize(
    "name,group",
    [
        pytest.param('SpanGroup', SpanGroup.add_all([(0, 0)]), id='str-span'),
    ],
)
def test_representation(name, group):
    assert name == repr(group)
