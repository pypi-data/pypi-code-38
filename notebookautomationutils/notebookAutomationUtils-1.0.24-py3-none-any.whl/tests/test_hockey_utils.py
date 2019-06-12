import os
import unittest
import utils.hockey_utils as hockey_utils
from unittest.mock import patch, Mock
from unittest import TestCase

class TestHockeyAppUtils(TestCase):
    """
    Tests for hockey app utils
    """
    def test_get_app_version(self):
        app_link = "https://rink.hockeyapp.net/manage/apps/31029/app_versions/7432"
        expected = dict()
        expected = {'version': '17.0',
                    'build': '6136089'}
        result = hockey_utils.get_app_version(app_link)
        assert result == expected

    def test_get_app_version_empty_link(self):
        app_link = ""
        result = hockey_utils.get_app_version(app_link)
        assert result == None 

    def test_get_app_version_null_link(self):
        app_link = None
        result = hockey_utils.get_app_version(app_link)
        assert result == None    