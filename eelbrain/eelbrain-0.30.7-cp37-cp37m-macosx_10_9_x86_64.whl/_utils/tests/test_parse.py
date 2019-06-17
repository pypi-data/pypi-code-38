# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
from nose.tools import eq_

from eelbrain._utils.parse import find_variables


def test_find_variables():
    eq_(find_variables("a + b / c.x()"), {'a', 'b', 'c'})
    eq_(find_variables("a + 'b' / c.x()"), {'a', 'c'})
