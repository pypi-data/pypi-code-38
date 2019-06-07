# Tai Sakuma <tai.sakuma@gmail.com>
import pytest

from qtwirl._parser.inputs import parse_data

##__________________________________________________________________||
@pytest.mark.parametrize('arg, expected', [
    pytest.param(['A.root', 'B.root'], ['A.root', 'B.root'], id='list'),
    pytest.param('A.root', ['A.root'], id='string'),
    pytest.param([ ], [ ], id='empty-list'),
    pytest.param('', [ ], id='empty-string'),
])
def test_parse_data(arg, expected):
    assert expected == parse_data(arg)

##__________________________________________________________________||
