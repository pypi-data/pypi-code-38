
from burlap.files import file # pylint: disable=redefined-builtin
from burlap.user import user
from burlap.tests.functional_tests.base import TestCase

is_dir = file.is_dir

class UserTests(TestCase):

    def test_create_user(self):
        try:
            user.create('user1', create_home=False, password=False)
            assert user.exists('user1')
            assert not is_dir('/home/user1')
        finally:
            user.sudo('userdel -r user1')
