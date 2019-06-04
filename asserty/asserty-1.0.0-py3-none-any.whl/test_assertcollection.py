from . import assert_that


def test_has_length_on_list():
    assert_that([]).has_length(0)
    assert_that([1]).has_length(1)
    assert_that([1]).not_has_length(2)
    assert_that([1]).has_length([2])


def test_has_length_on_dict():
    assert_that({}).has_length(0)
    assert_that({"a": 1}).has_length(1)
    assert_that({"a": 1}).has_length({"b": 2})
    assert_that({"a": 1}).not_has_length(2)


def test_has_length_on_str():
    assert_that("str").has_length(3)


def test_contains():
    assert_that([1, 2, 3]).contains(1)
    assert_that([1, 2, 3]).not_contains(4)


def test_contains_key():
    assert_that({"a": 1}).contains_key("a")
    assert_that({"a": 1}).not_contains_key("b")
    
    # With value
    assert_that({"a": 1}).contains_key_with_value("a", 1)


def test_has_same_elements_as():
    assert_that([1,2,3]).has_same_elements_as([2,1,3])

