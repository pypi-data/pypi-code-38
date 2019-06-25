from app import create_app
from app.config import app_env
from flask_testing import TestCase

app = create_app()


class BaseTestCase(TestCase):
    def create_app(self):
        app.config.from_object(app_env.get('testing'))
        return app

    def setUp(self):
        pass

    def tearDown(self):
        pass
