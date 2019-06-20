
from flaskeztest.eztestcase import EZTestCase


class TestCase1(EZTestCase):
    FIXTURE = 'oneuser'

    def runTest(self):
        self.navigate('/one')
        self.assertTrue(self.page.has_current_path("/one"))
        self.assertTrue(self.page.has_text('Bob'))

        self.assert_field_exists('User', 'name')
        self.assert_field_exists('User', 'name')


class TestCase2(EZTestCase):
    FIXTURE = 'oneuser'

    def runTest(self):
        self.navigate('/one')
        self.assertTrue(self.page.has_current_path("/one"))
        self.assertTrue(self.page.has_text('Bob'))

        self.assert_field_exists('User', 'name')
        self.assert_field_is_hidden('User', 'name')
