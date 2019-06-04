from . import expected_error


def test_expect_error():
    with expected_error(ZeroDivisionError):
        1 / 0


def test_expect_error_wrong_given_type():
    try:
        with expected_error(TypeError):
            1 / 0
    except ZeroDivisionError:
        pass
    