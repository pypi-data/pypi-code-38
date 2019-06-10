from unittest import TestCase
import tempfile, shutil
from faker import Factory as Faker_factory
from chibi.file.snippets import current_dir, cd, join, mkdir
from chibi.file import Chibi_file


faker = Faker_factory.create()


class Test_with_files( TestCase ):
    amount_of_files = 3
    amount_of_dirs = 3
    amount_of_files_with_content = 3
    amount_of_inner_dirs = 3

    defined_folders = []
    defined_files = []

    def setUp(self):
        self.root_dir = tempfile.mkdtemp()
        self.empty_folder = tempfile.mkdtemp()
        self.folder_with_files_with_content = tempfile.mkdtemp()

        self.files = [
            tempfile.mkstemp( dir=self.root_dir )[1]
            for i in range( self.amount_of_files ) ]
        self.dirs = [
            tempfile.mkdtemp( dir=self.root_dir )
            for i in range( self.amount_of_dirs ) ]
        for dir_level_1 in self.dirs:
            for i in range( self.amount_of_inner_dirs ):
                tempfile.mkdtemp( dir=dir_level_1 )

        self.files_with_content = []
        for i in range( self.amount_of_files_with_content ):
            file_path = tempfile.mkstemp(
                dir=self.folder_with_files_with_content )[1]
            with open( file_path, 'w' ) as new_file:
                new_file.write(
                    faker.text(max_nb_chars=200, ext_word_list=None) )
            self.files_with_content.append( file_path )


        for f in self.defined_folders:
            mkdir( join( self.root_dir, f ), verbose=False )

        for f in self.defined_files:
            Chibi_file( join( self.root_dir, f ) )

    def tearDown(self):
        shutil.rmtree( self.root_dir )
        shutil.rmtree( self.empty_folder )
        shutil.rmtree( self.folder_with_files_with_content )


class Test_moving_dir( TestCase ):
    def setUp( self ):
        self.origin_dir = current_dir()

    def tearDown(self):
        cd( self.origin_dir )
