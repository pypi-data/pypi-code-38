from unittest import TestCase
from tests.snippet.files import Test_with_files

from chibi.file.image import Chibi_image

class Test_images( TestCase ):
    def setUp( self ):
        super().setUp()
        self.jpg_path = './tests/file/1529990793499.jpg'
        self.png_path = './tests/file/1535359854403.png'
        self.gif_path = './tests/file/1536637012160.gif'

        self.jpg = Chibi_image( self.jpg_path )
        self.png = Chibi_image( self.png_path )
        self.gif = Chibi_image( self.gif_path )


class Test_eq( Test_images ):
    def test_can_open_the_images( self ):
        self.assertTrue( self.jpg.exists )
        self.assertTrue( self.png.exists )
        self.assertTrue( self.gif.exists )

        self.assertFalse( self.jpg.is_empty )
        self.assertFalse( self.png.is_empty )
        self.assertFalse( self.gif.is_empty )

    def test_should_return_resolution( self ):
        self.assertEqual( self.jpg.dimension, ( 498, 397 ) )
        self.assertEqual( self.png.dimension, ( 418, 498 ) )
        self.assertEqual( self.gif.dimension, ( 728, 720 ) )

    def test_should_get_the_correct_type( self ):
        self.assertEqual( self.jpg.properties.type, 'raster-image' )
        self.assertEqual( self.png.properties.type, 'raster-image' )
        self.assertEqual( self.gif.properties.type, 'raster-image' )

    def test_should_get_the_correct_mime( self ):
        self.assertEqual( self.jpg.properties.mime, 'image/jpeg' )
        self.assertEqual( self.png.properties.mime, 'image/png' )
        self.assertEqual( self.gif.properties.mime, 'image/gif' )

    def test_should_get_the_correct_extention( self ):
        self.assertEqual( self.jpg.properties.extension, 'jpg' )
        self.assertEqual( self.png.properties.extension, 'png' )
        self.assertEqual( self.gif.properties.extension, 'gif' )

    def test_should_be_equal( self ):
        self.assertEqual( self.jpg, self.jpg )
        self.assertEqual( self.gif, self.gif )
        self.assertEqual( self.png, self.png )

    def test_should_be_no_equal( self ):
        self.assertNotEqual( self.jpg, self.gif )
        self.assertNotEqual( self.jpg, self.png )

        self.assertNotEqual( self.gif, self.png )
        self.assertNotEqual( self.gif, self.jpg )

        self.assertNotEqual( self.png, self.jpg )
        self.assertNotEqual( self.png, self.gif )


class Test_thumbnails( Test_images, Test_with_files ):
    def test_create_in_diferent_folder( self ):
        thumbnail = self.jpg.thumbnail( self.root_dir )
        self.assertNotEqual( thumbnail.path, self.jpg.path )
        self.assertNotEqual( thumbnail, self.jpg.path )
