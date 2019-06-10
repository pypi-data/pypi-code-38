from django.test import TestCase

from chibi_user.models import User


class Test_user( TestCase ):
    def test_the_email_can_be_none( self ):
        user = User.objects.create_user(
            username='test', password='password', email=None )
        user_from_db = User.objects.get( pk=user.pk )
        self.assertEquals( user_from_db.pk, user.pk )

    def test_if_the_email_is_none_can_be_repeat( self ):
        user = User.objects.create_user(
            username='test', password='password', email=None )
        user_2 = User.objects.create_user(
            username='test_2', password='password', email=None )
        self.assertNotEqual( user.pk, user_2.pk )
        self.assertIsNone( user.email )
        self.assertIsNone( user_2.email )
