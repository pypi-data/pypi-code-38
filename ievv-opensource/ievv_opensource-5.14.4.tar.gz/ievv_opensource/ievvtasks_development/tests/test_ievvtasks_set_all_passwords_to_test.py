from django.conf import settings
from django.contrib.auth import get_user_model

from django.core import management
from django.test import TestCase
from model_mommy import mommy


class TestSetAllPasswordsToTest(TestCase):
    def test_set_all_password_to_test(self):
        user1 = mommy.make(settings.AUTH_USER_MODEL)
        user1.set_password('old')
        user2 = mommy.make(settings.AUTH_USER_MODEL)
        user2.set_password('old')
        management.call_command('ievvtasks_set_all_passwords_to_test')
        self.assertTrue(
            get_user_model().objects.get(id=user1.id).check_password('test'))
        self.assertTrue(
            get_user_model().objects.get(id=user2.id).check_password('test'))
