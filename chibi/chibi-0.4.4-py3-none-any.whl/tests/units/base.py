from chibi.units.base import Unit
from unittest import TestCase


class Test_unit( TestCase ):
    def setUp( self ):
        self.unit = Unit( 10 )

    def test_should_print_the_value_when_is_str( self ):
        self.assertIn( '10', str( self.unit ) )

    def test_when_add_a_int_should_work( self ):
        r = 10 + self.unit
        self.assertEqual( r.value, 20 )
        r = self.unit + 10
        self.assertEqual( r.value, 20 )

    def test_when_add_a_float_should_work( self ):
        r = 10.10 + self.unit
        self.assertEqual( r.value, 20.1 )
        r = self.unit + 10.1
        self.assertEqual( r.value, 20.1 )

    def test_when_sub_a_int_should_work( self ):
        r = 10 - self.unit
        self.assertEqual( r.value, 0 )
        r = self.unit - 10
        self.assertEqual( r.value, 0 )

    def test_when_sub_a_float_should_work( self ):
        r = 10.10 - self.unit
        self.assertAlmostEqual( r.value, -0.1, delta=0.01 )
        r = self.unit - 10.10
        self.assertAlmostEqual( r.value, -0.1, delta=0.01 )

    def test_when_mul_a_int_should_work( self ):
        r = 10 * self.unit
        self.assertEqual( r.value, 100 )
        r = self.unit * 10
        self.assertEqual( r.value, 100 )

    def test_when_mul_a_float_should_work( self ):
        r = 10.1 * self.unit
        self.assertEqual( r.value, 101.0 )
        r = self.unit * 10.1
        self.assertEqual( r.value, 101.0 )

    def test_when_div_a_int_should_work( self ):
        r = 10 / self.unit
        self.assertEqual( r.value, 1 )
        r = self.unit / 10
        self.assertEqual( r.value, 1 )

    def test_when_div_a_float_should_work( self ):
        r = 10.10 / self.unit
        self.assertAlmostEqual( r.value, 0.99, delta=0.001 )
        r = self.unit / 10.10
        self.assertAlmostEqual( r.value, 0.99, delta=0.001 )

    def test_when_div_int_a_int_should_work( self ):
        r = 10 // self.unit
        self.assertEqual( r.value, 1 )
        r = self.unit // 10
        self.assertEqual( r.value, 1 )

    def test_when_div_int_a_float_should_work( self ):
        r = 10.10 // self.unit
        self.assertEqual( r.value, 0 )
        r = self.unit // 10.10
        self.assertEqual( r.value, 0 )

    def test_when_pow_a_int_should_work( self ):
        r = 10 ** self.unit
        self.assertEqual( r.value, 10000000000 )
        r = self.unit ** 10
        self.assertEqual( r.value, 10000000000 )

    def test_when_pow_float_a_float_should_work( self ):
        r = 10.10 ** self.unit
        self.assertEqual( r.value, 12589254117.941662 )
        r = self.unit ** 10.10
        self.assertEqual( r.value, 12589254117.941662 )
