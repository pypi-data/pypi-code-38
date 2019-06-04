from . import assert_that


def test_is_true():
    assert_that(True).is_true()
    assert_that(1 == 1).is_true()


def test_is_not_true():
    assert_that(False).is_not_true()


def test_is_false():
    assert_that(False).is_false()


def test_is_not_false():
    assert_that(True).is_not_false()
