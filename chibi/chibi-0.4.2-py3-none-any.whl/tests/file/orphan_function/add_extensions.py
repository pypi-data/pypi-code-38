from tests.snippet.files import Test_with_files
from chibi.file.snippets import add_extensions
from chibi.file.path import Chibi_path


class Test_add_extensions( Test_with_files ):
    def test_should_add_thumbnail( self ):
        result = add_extensions( "image.jpg", "thumbnail" )
        expected = "image.thumbnail.jpg"
        self.assertEqual( result, expected )

    def test_should_return_a_chibi_path( self ):
        result = add_extensions( "image.jpg", "thumbnail" )
        self.assertIsInstance( result, Chibi_path )
