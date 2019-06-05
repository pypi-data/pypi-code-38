from pkg_resources import require
require("mock>=1.0.1")
from unittest import TestCase

from mock import Mock, patch, call


from CrystalMatch.dls_util.imaging.color import Color


class TestColor(TestCase):

    def test_default_alpha_value_is_255(self):
        col = Color(0, 56.7, 255)
        self.failUnlessEqual(0, col.r)
        self.failUnlessEqual(56, col.g)
        self.failUnlessEqual(255, col.b)
        self.failUnlessEqual(255, col.a)

    def test_init_with_invalid_values_raises_error(self):
        self.failUnlessRaises(TypeError, Color, None, 2, 3, 4)
        self.failUnlessRaises(ValueError, Color, 1, "not_a_number", 3, 4)
        self.failUnlessRaises(ValueError, Color, 1, 2, 256, 4)
        self.failUnlessRaises(ValueError, Color, 1, 2, 3, -5.4)

    def test_to_string_has_correct_format(self):
        col = Color(46, 0, 255, 123)
        self.failUnlessEqual("46,0,255,123", str(col))

    def test_true_string_representation_has_correct_format(self):
        col = Color(46, 0, 255, 123)
        self.failUnlessEqual("Color(46, 0, 255, 123)", repr(col))

    def test_open_cv_bgra_format(self):
        col = Color(46, 0, 255, 123)
        b, g, r, a = col.bgra()
        self.failUnlessEqual(b, 255)
        self.failUnlessEqual(g, 0)
        self.failUnlessEqual(r, 46)
        self.failUnlessEqual(a, 123)
        b, g, r = col.bgr()
        self.failUnlessEqual(b, 255)
        self.failUnlessEqual(g, 0)
        self.failUnlessEqual(r, 46)

    def test_convert_to_8_bit_greyscale(self):
        self.validate_and_return_luma_value(46, 23, 255)
        self.validate_and_return_luma_value(255, 255, 255)
        self.validate_and_return_luma_value(0, 0, 0)
        self.validate_and_return_luma_value(200, 16, 36)

    def test_8_bit_greyscale_value_unaffected_by_alpha_value(self):
        array = [self.validate_and_return_luma_value(35, 27, 195, 0),
                 self.validate_and_return_luma_value(35, 27, 195, 50),
                 self.validate_and_return_luma_value(35, 27, 195, 150),
                 self.validate_and_return_luma_value(35, 27, 195, 255)]
        self.failUnlessEqual([78, 78, 78, 78], array)

    def validate_and_return_luma_value(self, b, g, r, a=255):
        col = Color(r, g, b, a)
        luma_value = int(round(0.299 * r + 0.587 * g + 0.114 * b))
        self.failUnlessEqual(luma_value, col.mono())
        self.failIf(luma_value < 0)
        self.failIf(luma_value > 255)
        return luma_value

    def test_hex_conversion(self):
        self.failUnlessEqual("#4286f4", Color(66, 134, 244).to_hex())
        self.failUnlessEqual("#071223", Color(7, 18, 35).to_hex())
        self.failUnlessEqual("#8e2525", Color(142, 37, 37).to_hex())
        self.failUnlessEqual("#1c8415", Color(28, 132, 21).to_hex())

    def test_colour_from_string_with_rgb_values(self):
        self.failUnlessEqual(Color(123, 234, 45), Color.from_string("123,234,45"))

    def test_colour_from_string_with_rgb_values_plus_alpha(self):
        self.failUnlessEqual(Color(123, 234, 45, 255), Color.from_string("123,234,45,255"))

    def test_colour_from_string_is_whitespace_indifferent(self):
        self.failUnlessEqual(Color(123, 234, 45), Color.from_string("123, 234,    45"))
        self.failUnlessEqual(Color(123, 234, 45, 255), Color.from_string("123,  234,    45,  255"))

    def test_colour_from_string_with_explicit_separator(self):
        self.failUnlessEqual(Color(123, 234, 45, 255), Color.from_string("123; 234;45;  255", sep=";"))

    def test_colour_from_string_with_invalid_value_raises_error(self):
        self.failUnlessRaises(ValueError, Color.from_string, "123,234,45,25d5")
        self.failUnlessRaises(ValueError, Color.from_string, "45,255")
        self.failUnlessRaises(ValueError, Color.from_string, "455")
        self.failUnlessRaises(ValueError, Color.from_string, "123,,45,255")

    def test_colour_from_string_with_null_value_raises_error(self):
        self.failUnlessRaises(TypeError, Color.from_string, None)

    def test_equality_operator(self):
        self.failUnless(Color(1, 2, 3, 4) == Color(1, 2, 3, 4))
        self.failIf(Color(1, 2, 3, 4) == Color(0, 2, 3, 4))
        self.failIf(Color(1, 2, 3, 4) == Color(1, 0, 3, 4))
        self.failIf(Color(1, 2, 3, 4) == Color(1, 2, 0, 4))
        self.failIf(Color(1, 2, 3, 4) == Color(1, 2, 3, 0))

    def test_equality_operator_fail_with_invalid_type(self):
        null_var = None
        color = Color(1, 2, 3, 4)
        self.failUnlessRaises(TypeError, color.__eq__, null_var)
        self.failUnlessRaises(TypeError, color.__eq__, "Not a Color")
        self.failUnlessRaises(TypeError, color.__eq__, 4.6)

    # noinspection PyUnusedLocal
    @patch('CrystalMatch.dls_util.imaging.color.randint', return_value=100)
    def test_random_generation_of_colour(self, mock_randint):
        expected = Color(100, 100, 100, 255)
        generated = Color.random()
        mock_randint.assert_has_calls([
            call(0, 255),
            call(0, 255),
            call(0, 255)
        ])
        self.failUnlessEqual(expected, generated)
