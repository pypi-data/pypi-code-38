import random

from faker import Factory as Faker_factory

from chibi.file.snippets import move, exists, join, ls, get_file_from_path
from tests.snippet.files import Test_with_files


faker = Faker_factory.create()


class Test_move( Test_with_files ):
    def test_when_move_a_empty_file_should_create_a_new_empty_file( self ):
        file = random.choice( self.files )
        dest = join( self.root_dir, faker.file_name() )
        self.assertFalse( exists( dest ) )
        with open( file ) as file_str:
            self.assertFalse( file_str.read() )

        move( file, dest )
        self.assertFalse( exists( file ) )
        with open( dest ) as file_dest:
            self.assertFalse( file_dest.read() )

    def test_when_move_a_file_with_content_should_have_the_content( self ):
        file = random.choice( self.files_with_content )
        dest = join( self.root_dir, faker.file_name() )
        self.assertFalse( exists( dest ) )
        with open( file ) as file_src:
            str_data = file_src.read()

        move( file, dest )
        self.assertFalse( exists( file ) )
        with open( dest ) as file_dest:
            self.assertEqual( str_data, file_dest.read() )

    def test_when_move_with_wild_card_should_move_all_the_files( self ):
        dir = random.choice( self.files_with_content )
        self.assertTrue( list( ls( self.folder_with_files_with_content ) ) )
        files = list( ls( self.folder_with_files_with_content ) )
        move( join( self.folder_with_files_with_content, '*' ), self.root_dir )
        for f in files:
            self.assertFalse( exists( f ) )

        files = [ get_file_from_path( f ) for f in files ]

        for f in files:
            self.assertTrue( exists( join( self.root_dir, f ) ) )
