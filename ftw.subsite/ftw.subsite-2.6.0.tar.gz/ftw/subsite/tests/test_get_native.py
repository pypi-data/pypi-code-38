from ftw.subsite.languages import translate_language
from ftw.subsite.testing import FTW_SUBSITE_INTEGRATION_TESTING
import unittest2 as unittest


class TestGetLanguageNative(unittest.TestCase):

    layer = FTW_SUBSITE_INTEGRATION_TESTING

    def test_return_native_for_existing_language(self):
        """Test If our function returns the correct Native, if the Language
        exists"""
        native = translate_language(self.layer['portal'], 'sv')
        self.assertEqual(u'Svenska', native)

    def test_returns_none_for_invalid_language(self):
        """Check if function returns nothing when the language
        doesn't exist.'"""
        native = translate_language(self.layer['portal'], 'hans')
        self.assertEqual(None, native)
