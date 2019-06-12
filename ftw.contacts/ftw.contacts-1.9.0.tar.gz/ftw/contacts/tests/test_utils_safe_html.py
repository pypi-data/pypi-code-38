from ftw.contacts.testing import FTW_CONTACTS_FUNCTIONAL_TESTING
from ftw.contacts.utils import safe_html
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest2 import TestCase


class TestSafeHtml(TestCase):

    layer = FTW_CONTACTS_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_returns_safe_html(self):
        self.assertEquals(
            'Ch\xc3\xa4ck',
            safe_html('<script>bad code</script>Ch\xc3\xa4ck'))

    def test_returns_empty_string_if_text_is_None(self):
        self.assertEquals('', safe_html(None))

    def test_returns_safe_html_with_unicode(self):
        self.assertEquals(
            'Ch\xc3\xa4ck',
            safe_html(u'<script>bad</script>Ch\xe4ck'))

    def test_transform_nl_to_br(self):
        self.assertEquals(
            'Ch\xc3\xa4ck<br />',
            safe_html('<script>bad</script>Ch\xc3\xa4ck\n'))
