from django.test import TestCase
from chibi_user.factories import Token as Token_factory
from chibi_user.models import (
    Token as Token_model,
    User as User_model,
)


class Test_token( TestCase ):
    def test_factory( self ):
        token = Token_factory.build()
        self.assertIsInstance( token, Token_model )
        self.assertIsInstance( token.user, User_model )
