from django.test import TestCase
from chibi_user.factories import User as User_factory
from chibi_user.models import (
    Token as Token_model,
    User as User_model,
)


class Test_users( TestCase ):
    def test_factory( self ):
        user = User_factory.build()
        self.assertIsInstance( user, User_model )
        self.assertIsInstance( user.token, Token_model )
