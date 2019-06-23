"""
unit tests
"""
from kawhi import say_hello


def test_say_hello_no_params():
    """ no arguments test """
    assert (say_hello()) == "Hello, Kawhi!"


def test_say_hello_with_param():
    """ no arguments test """
    assert (say_hello("John")) == "Hello, Kawhi - This is John."
