from unittest import TestCase
from chibi import madness


class Test_generate_token_b64( TestCase ):
    def test_should_no_return_a_empty_string( self ):
        self.assertTrue( madness.string.generate_token_b64 )


class Test_generate_b64_unsecure( TestCase ):
    def test_should_no_return_a_empty_string( self ):
        self.assertTrue( madness.string.generate_b64_unsecure )


class Test_generate_string( TestCase ):
    def test_should_no_return_a_empty_string( self ):
        self.assertTrue( madness.string.generate_string )


class Test_generate_email( TestCase ):
    def test_should_no_return_a_empty_string( self ):
        self.assertTrue( madness.string.generate_email )


class Test_generate_password( TestCase ):
    def test_should_no_return_a_empty_string( self ):
        self.assertTrue( madness.string.generate_password )
