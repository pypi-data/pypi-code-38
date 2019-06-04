from . import assert_that


def test_when_called_returns():
    def razor():
        return 1
    assert_that(razor).when_called.returns(1)


def test_when_called_raises():
    def razor():
        raise TypeError()
    assert_that(razor).when_called.raises(TypeError)


def test_when_called_with_returns():
    def razor(int_arg):
        return int_arg * 2

    assert_that(razor).when_called_with(1).returns(2)


def test_when_called_with_raises():
    def razor(arg):
        if not isinstance(arg, str):
            raise TypeError()

    assert_that(razor).when_called_with(1).raises(TypeError)
    assert_that(razor).if_called_with(1).raises(TypeError)
    try:
        assert_that(razor).if_called_with("str").raises(TypeError)
        assert False, "did not raise exception"
    except AssertionError:
        pass


def test_callable_example():
    def func(arg):
        if not isinstance(arg, str):
            raise TypeError()
        return arg + "yay"

    assert_that(func).when_called_with(1).raises(TypeError)
    assert_that(func).if_called_with("Hey-").returns("Hey-yay")
