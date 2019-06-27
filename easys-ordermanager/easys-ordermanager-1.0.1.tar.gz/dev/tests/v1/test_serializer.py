import json
import os

from django.conf import settings
from unittest import TestCase

from easys_ordermanager.v1.serializer import Serializer


class SerializerV1TestCase(TestCase):
    def setUp(self):
        with open(os.path.join(settings.BASE_DIR, 'dev', 'tests', 'v1', 'example.json'), 'r') as f:
            self.fixture = json.load(f)

    def test_validate_data(self):
        s = Serializer()
        self.assertTrue(s.validate(self.fixture))
