from tests.snippet.files import Test_with_files
from chibi.file import Chibi_file


class Test_chibi_file_properties( Test_with_files ):
    def setUp( self ):
        super().setUp()
        self.chibi_file = Chibi_file( self.files_with_content[0] )

    def test_file_name( self ):
        self.assertIn( self.chibi_file.file_name, self.chibi_file.path )
        self.assertNotEqual( self.chibi_file.file_name, self.chibi_file.path )

    def test_dir( self ):
        self.assertIn( self.chibi_file.dir , self.chibi_file.path )
        self.assertNotEqual( self.chibi_file.dir , self.chibi_file.path )
