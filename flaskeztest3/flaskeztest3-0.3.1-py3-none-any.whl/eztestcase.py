"""EZTestCase class as well as its subclasses used be eztest package defined here."""

from unittest import TestCase

from flask import url_for
import capybara.dsl
import capybara


class EZTestCase(TestCase):
    """Test cases that should be ran with flaskeztest 'eztest' command should inherit from this class."""
    NAME = None
    FIXTURE = None

    def __init__(self, eztest, method_name='runTest'):
        TestCase.__init__(self, method_name)
        self.eztest = eztest
        self.page = None
        self.driver = None
        self.base_url = 'http://localhost:5000'
        self.wait_time = 1  # Default
        self.name = self.__class__.NAME
        self.fixture = self.__class__.FIXTURE
        self.expected_models = dict()

    def setUp(self):
        self.page = capybara.dsl.page
        self.driver = self.page.driver.browser
        self.driver.implicitly_wait(self.wait_time)
        self.eztest.reset_db()
        if self.fixture is not None:
            self.load_fixture()

    def tearDown(self):
        capybara.reset_sessions()

    def get_endpoint(self, endpoint, **endpoint_kwargs):
        with self.eztest.app.app_context():
            self.page.visit(url_for(endpoint, **endpoint_kwargs))

    def load_fixture(self):
        self.expected_models = self.eztest.load_fixture(self.fixture)

    def does_field_exist(self, model, field, row_index=None):
        if row_index is not None:
            return self.page.has_text(self.expected_models[model][row_index][field])
        else:
            return self.page.has_text(self.expected_models[model][field])

    def is_field_visible(self, model, field, row_index=None):
        element = self.get_element_for_field(model, field, row_index)
        return element.visible

    def get_element_for_field(self, model, field, row_index=None):
        if row_index is not None:
            return self.page.find('xpath', '*//*[text()="%s"]' % self.expected_models[model][row_index][field])
        else:
            return self.page.find('xpath', '*//*[text()="%s"]' % self.expected_models[model][field])
