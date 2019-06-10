import random

from faker import Factory as Faker_factory

from chibi.file.snippets import copy, exists, join, copy_folder, delete, ls
from tests.snippet.files import Test_with_files


faker = Faker_factory.create()


class Test_copy( Test_with_files ):
    def test_when_copy_a_empty_file_should_create_a_new_empty_file( self ):
        file = random.choice( self.files )
        dest = join( self.root_dir, faker.file_name() )
        self.assertFalse( exists( dest ) )

        copy( file, dest )
        self.assertTrue( exists( dest ) )
        with open( dest ) as file_dest:
            self.assertFalse( file_dest.read() )

    def test_when_copy_a_file_with_content_should_copy_the_content( self ):
        file = random.choice( self.files_with_content )
        dest = join( self.root_dir, faker.file_name() )
        self.assertFalse( exists( dest ) )

        copy( file, dest )
        self.assertTrue( exists( dest ) )
        with open( dest ) as file_dest:
            with open( file ) as file_src:
                self.assertEqual( file_src.read(), file_dest.read() )


class Test_copy_folder( Test_with_files ):
    def test_should_copy_all_the_folder( self ):
        dest = join( self.root_dir, 'hola' )
        self.assertFalse( exists( dest ) )
        copy_folder( self.folder_with_files_with_content, dest )
        self.assertTrue( exists( dest ) )

        self.assertEqual(
            len( set( ls( self.folder_with_files_with_content ) ) ),
            len( set( ls( dest ) ) ) )
