from chibi.units.si import Metre, Gram
from unittest import TestCase
from .base import Test_unit


class Test_Metre( Test_unit ):
    def setUp( self ):
        self.unit = Metre( 10 )


class Test_Gram( Test_unit ):
    def setUp( self ):
        self.unit = Gram( 10 )
