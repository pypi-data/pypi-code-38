from unittest import TestCase
from chibi.object import Chibi_object
from chibi.object.descriptor import Descriptor


class Test_descriptor( TestCase ):

    def test_descriptor_init( self ):
        d = Descriptor()
        self.assertIsNone( d.name )
        self.assertFalse( d.required )
        self.assertIsNone( d.default )

    def test_descriptor_default( self ):
        d = Descriptor( default='asdf' )
        self.assertIsNone( d.name )
        self.assertFalse( d.required )
        self.assertEqual( d.default, 'asdf' )
