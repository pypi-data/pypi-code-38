import random

from faker import Factory as Faker_factory

from chibi.file import Chibi_file
from chibi.file.snippets import join, exists
from tests.snippet.files import Test_with_files


faker = Faker_factory.create()


class Test_copy( Test_with_files ):
    def test_when_copy_a_empty_file_should_create_a_new_empty_file( self ):
        file = random.choice( self.files )
        dest = join( self.root_dir, faker.file_name() )
        self.assertFalse( exists( dest ) )

        cf = Chibi_file( file )
        cf.copy( dest, verbose=False )
        self.assertTrue( exists( dest ) )
        with open( dest ) as file_dest:
            self.assertFalse( file_dest.read() )

    def test_when_copy_a_file_with_content_should_copy_the_content( self ):
        file = random.choice( self.files_with_content )
        dest = join( self.root_dir, faker.file_name() )
        self.assertFalse( exists( dest ) )

        cf = Chibi_file( file )
        cf.copy( dest, verbose=False )
        self.assertTrue( exists( dest ) )
        with open( dest ) as file_dest:
            with open( file ) as file_src:
                self.assertEqual( file_src.read(), file_dest.read() )
