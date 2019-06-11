from pytest import raises
from toon.input.device import Obs


def test_obs():
    class SubObs(Obs):
        shape = (3, 2)
        ctype = float

    good_data = [[1, 2], [3, 4], [5, 6]]
    flat_data = [1, 2, 3, 4, 5, 6]
    bad_data = [[1, 2], [3, 4]]
    wrong_type = [['a', 'b'], ['c', 'd'], ['d', 'e']]

    subobs = SubObs(time=3, data=good_data)
    # flat (coerced to correct shape by the shape property)
    subobs2 = SubObs(time=3, data=flat_data)
    assert((subobs.data == subobs2.data).all())

    # wrong time type
    with raises(ValueError):
        x = SubObs(time='s', data=good_data)

    # wrong data shape
    with raises(ValueError):
        x = SubObs(time=3, data=bad_data)

    # wrong data type
    with raises(ValueError):
        x = SubObs(time=3, data=wrong_type)
