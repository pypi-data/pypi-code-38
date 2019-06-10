from unittest import TestCase
from chibi.object import Chibi_object
from chibi.atlas import Chibi_atlas

from chibi.module import import_, export


class Test_import( TestCase ):

    def setUp( self ):
        pass

    def test_import_chibi_object( self ):
        cls = import_( 'chibi.object.Chibi_object' )
        self.assertEqual( cls, Chibi_object )

    def test_import_chibi_atlas( self ):
        cls = import_( 'chibi.atlas.Chibi_atlas' )
        self.assertEqual( cls, Chibi_atlas )


class Test_export( TestCase ):

    def setUp( self ):
        pass

    def test_import_chibi_object( self ):
        cls = 'chibi.object.object.Chibi_object'
        self.assertEqual( cls, export( Chibi_object ) )

    def test_import_chibi_atlas( self ):
        cls = 'chibi.atlas.Chibi_atlas'
        self.assertEqual( cls, export( Chibi_atlas ) )
