from tests.snippet.files import Test_with_files
from chibi.file import Chibi_file


class Test_chibi_file_append( Test_with_files ):
    def setUp( self ):
        super().setUp()
        self.chibi_file = Chibi_file( self.files_with_content[0] )

    def test_should_add_more_text( self ):
        self.chibi_file
        whole_file = "".join( self.chibi_file.chunk() )
        self.assertTrue( whole_file, "el archivo esta vacio" )
        self.chibi_file.append( 'explosion!!!' )
        whole_file_before = "".join( self.chibi_file.chunk() )
        self.assertNotEqual( whole_file, whole_file_before )
        self.assertGreater( whole_file_before, whole_file )
