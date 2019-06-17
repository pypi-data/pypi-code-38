from django.test import TestCase


class BasicTest(TestCase):

    def test_dummy(self):
        self.assertEqual(1 + 1, 2)
