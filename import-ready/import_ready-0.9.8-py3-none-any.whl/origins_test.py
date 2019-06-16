""" pytest unit tests for the origins module"""
from . import origins

def test_founder():
    """ unit test origins.founder """
    who = origins.founder()
    names = who.split()
    first = names[0]
    last = names[1]
    assert first == 'Rick'
    assert last == 'Hovac'

def test_established():
    """ unit test origins.established """
    when = origins.established()
    assert when[:8] == 'Not 2004'
