import pytest

from ..replacement import Replacement


@pytest.mark.parametrize(
    "input_tuple",
    [
        pytest.param((10, 15, '薄餡亂入'), id='str-replacement'),
        pytest.param((10, 15, '薄餡亂入', 'ohoh'), id='str-replacement with annotation'),
        pytest.param((10, 15, ['薄餡亂入']), id='list-replacement'),
        pytest.param((10, 15, ['薄餡亂入'], 'ohoh'), id='list-replacement with annotation'),
    ],
)
def test_correctly_init(input_tuple):
    replacement = Replacement(*input_tuple)

    start = input_tuple[0]
    end = input_tuple[1]
    new_value = input_tuple[2]
    annotation = None
    if len(input_tuple) == 4:
        annotation = input_tuple[3]

    assert start == replacement.start
    assert end == replacement.end
    assert new_value == replacement.new_value
    assert annotation == replacement.annotation


@pytest.mark.parametrize(
    "obj1,obj2",
    [
        pytest.param((10, 15, '薄餡亂入'), (10, 15, '薄餡亂入'),
                     id='no annotation'),
        pytest.param((10, 15, '薄餡亂入', '1'), (10, 15, '薄餡亂入', '2'),
                     id='different annotation'),
    ],
)
def test_equal(obj1, obj2):
    assert Replacement(*obj1) == Replacement(*obj2)


@pytest.mark.parametrize(
    "obj1,obj2",
    [
        pytest.param((10, 15, '薄餡亂入'), (10, 15, '隼興亂入'), id='different new_value'),
        pytest.param((10, 15, '薄餡亂入'), (9, 15, '薄餡亂入'), id='different start index'),
        pytest.param((10, 15, '薄餡亂入'), (10, 11, '薄餡亂入'), id='different end index'),
        pytest.param((10, 15, ['薄餡亂入']), (10, 15, '薄餡亂入'), id='different type of new_value'),
    ],
)
def test_not_equal(obj1, obj2):
    assert Replacement(*obj1) != Replacement(*obj2)


@pytest.mark.parametrize(
    "input_tuple,expected",
    [
        pytest.param((10, 15, '薄餡亂入'), "(10, 15) => '薄餡亂入'", id='str-replacement'),
        pytest.param((10, 15, ['薄餡亂入']),
                     "(10, 15) => '['薄餡亂入']'", id='lst-replacement'),
        pytest.param((10, 15, 10000),
                     "(10, 15) => '10000'", id='int-replacement'),
    ],
)
def test_str(input_tuple, expected):
    replacement = Replacement(*input_tuple)
    assert expected == str(replacement)


@pytest.mark.parametrize(
    "input_tuple,expected",
    [
        pytest.param((10, 15, '薄餡亂入'),
                     "Replacement(10, 15, 薄餡亂入, annotation=None)",
                     id='str-replacement no annotation'),
        pytest.param((10, 15, '薄餡亂入', 'ohoh'),
                     "Replacement(10, 15, 薄餡亂入, annotation=ohoh)",
                     id='str-replacement with annotation'),
        pytest.param((10, 15, ['薄餡亂入']),
                     "Replacement(10, 15, ['薄餡亂入'], annotation=None)",
                     id='lst-replacement no annotation'),
        pytest.param((10, 15, ['薄餡亂入'], 'ohoh'),
                     "Replacement(10, 15, ['薄餡亂入'], annotation=ohoh)",
                     id='lst-replacement with annotation'),
        pytest.param((10, 15, 10000),
                     "Replacement(10, 15, 10000, annotation=None)",
                     id='int-replacement no annotation'),
        pytest.param((10, 15, 10000, 'ohoh'),
                     "Replacement(10, 15, 10000, annotation=ohoh)",
                     id='int-replacement with annotation'),
    ],
)
def test_representation(input_tuple, expected):
    replacement = Replacement(*input_tuple)
    assert expected == repr(replacement)
