from config import config
from flask_testing import TestCase
from main import create_app

app = create_app(config.get('testing'))


class BaseTestCase(TestCase):
    def create_app(self):
        app.config.from_object(config.get('testing'))
        return app

    def setUp(self):
        pass

    def tearDown(self):
        pass
