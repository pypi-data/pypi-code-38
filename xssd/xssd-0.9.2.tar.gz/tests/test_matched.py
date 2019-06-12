"""
Simple match and notMatch testing
"""

from xssd.errors import (
    NO_ERROR, INVALID_MATCH,
)
from .base_tests import BaseFileTest, Static

class MatchTest(BaseFileTest):
    """Test for checking the simple match."""
    definition = {
        'root' : [
            {'name': 'password', 'type': 'string'},
            {'name': 'confirm', 'type': 'string', 'match': 'password'},
            {'name': 'notsame', 'type': 'string', 'notMatch': 'confirm'},
        ],
    }

    def test_01_correct(self):
        """Items Match Correctly"""
        # Odd should pass, Even should fail.
        data = {
            'password' : 'foo',
            'confirm'  : 'foo',
            'notsame'  : 'bar',
        }
        self.positive_test(data)

    def test_03_negative(self):
        """Items Match Incorrectly"""
        data = {
            'password' : 'foo',
            'confirm'  : 'bar',
            'notsame'  : 'bar',
        }
        errors = {
            'password' : NO_ERROR,
            'confirm' : INVALID_MATCH,
            'notsame' : INVALID_MATCH,
        }
        self.negative_test(data, errors)

class XpathTest(BaseFileTest):
    """Test with xpaths"""
    definition = Static({
        'root' : [
            {'name': 'password', 'type': 'string'},
            {'name': 'confirm', 'type': 'string', 'match': '/password'},
            {'name': 'notsame', 'type': 'string', 'notMatch': '/confirm'},
        ],
    })

    def test_01_root_match(self):
        """Match from the Root"""
        data = Static({
            'password' : 'foo',
            'confirm'  : 'foo',
            'notsame'  : 'bar',
        })
        self.positive_test(data)
