from . import assert_that


def test_equals_str():
    assert_that("str").equals("str")
    assert_that("str").not_equals("yo")


def test_equals_int():
    assert_that(1).equals(1)
    assert_that(2).not_equals(3)


def test_equals_float():
    assert_that(1.2).equals(1.2)
    assert_that(0.1).not_equals(-0.1)


def test_equals_with_same_class():
    class Tmp:
        def __init__(self, var):
            self.var = var
    t1 = Tmp(1)
    t2 = Tmp(2)
    assert_that(t1).equals(t1)
    assert_that(t1).not_equals(t2)


def test_equals_with_different_class():
    class Class1:
        def __init__(self, var):
            self.var = var
            
    class Class2:
        def __init__(self, var):
            self.var = var
    
    c1 = Class1(1)
    c2 = Class2(2)
    assert assert_that(c1).not_equals(c2)


def test_equals_with_list():
    a = [1]
    b = [1]
    assert_that(a).equals(b)
    assert_that(a).not_equals([3])


def test_equals_with_dict():
    a = {"a":1}
    b = {"a":1}
    assert_that(a).equals(b)
    assert_that(a).not_equals({"c":2})


def test_is_none():
    assert_that(None).is_none()
    assert_that("str").is_not_none()


def test_has_type_on_str():
    assert_that("str").has_type(str)
    assert_that("str").has_type("string")
    assert_that("str").not_has_type(int)
    assert_that("str").not_has_same_type_as(int)


def test_also():
    assert_that("str").equals("str").also.not_equals("string")


def test_and_do():
    assert_that("str").equals("str").and_do.not_equals("string")


def test_is_in():
    assert_that(1).is_in(range(10))
    assert_that(10).is_not_in(range(10))
    

def test_greater():
    assert_that(1).is_greater_than(0)
    assert_that(1).is_greater_or_equal_to(0)
    assert_that(1).is_greater_or_equal_to(1)
    

def test_less():
    assert_that(1).is_less_than(2)
    assert_that(1).is_less_or_equal_to(1)
    assert_that(1).is_less_or_equal_to(2)


def test_has_attribute():
    class MyClass:
        name = "MyClass"
    assert_that("str").has_attribute("__str__")
    assert_that(MyClass()).has_attribute("name")
    assert_that(MyClass()).has_attribute_with_value("name", "MyClass")


def test_chained():
    assert_that(5).is_in(range(10)).and_is.is_less_than(8)


def test_readme_examples():
    assert_that("str").not_equals("string")
    assert_that(5).is_in(range(10)).also.is_less_than(8)

    def myfunc(arg):
        if not isinstance(arg, str):
            raise TypeError()
        return arg+"yay"

    assert_that(myfunc).if_called_with(1).raises(TypeError)
    assert_that(myfunc).if_called_with("Hey-").returns("Hey-yay")