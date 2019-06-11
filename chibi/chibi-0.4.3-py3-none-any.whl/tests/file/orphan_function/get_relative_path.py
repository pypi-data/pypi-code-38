import random

from faker import Factory as Faker_factory

from chibi.file.snippets import copy, exists, common_root, get_relative_path
from tests.snippet.files import Test_with_files
from unittest import TestCase


class Test_get_relative_path( TestCase ):
    def test_should_return_the_relative_paths( self ):
        result = get_relative_path( '/usr/var/log', '/usr/var/security' )
        self.assertEqual( [ 'log', 'security' ], result  )

    def test_should_return_the_relative_path( self ):
        result = get_relative_path( '/usr/var/log', root='/usr/var' )
        self.assertEqual( 'log' , result  )
