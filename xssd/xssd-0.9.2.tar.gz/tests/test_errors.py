"""
Test all errors and structure errors.
"""

from unittest import TestCase
from xssd.base import MODE_AND, MODE_OR
from xssd.errors import (
    ElementErrors,
    NO_ERROR, INVALID_TYPE, INVALID_MINLENGTH, INVALID_MAXLENGTH
)

class TestErrorObject(TestCase):
    """Test the error objects created."""
    def test_no_error(self):
        """No Errors is a Sucess"""
        self.assert_(not NO_ERROR)

    def test_error(self):
        """Errors Fail"""
        self.assert_(INVALID_TYPE)

    def test_error_name(self):
        """Error Names"""
        self.assertEqual(str(INVALID_TYPE), "INVALID_NODE_TYPE")

    def test_error_id(self):
        """Error Enumeration"""
        self.assertEqual(int(INVALID_TYPE), 0x01)

    def test_error_compare(self):
        """Error Compare Against own Type"""
        self.assertEqual(INVALID_TYPE, INVALID_TYPE)

    def test_error_id_compare(self):
        """Error Compare Against ID"""
        self.assertEqual(INVALID_TYPE, 0x01)

    def test_error_not_compare(self):
        """Error Doesn't Compare"""
        self.assertNotEqual(INVALID_TYPE, INVALID_MAXLENGTH)

    def test_id_not_compare(self):
        """Error Doesn't Compare Against ID"""
        self.assertNotEqual(INVALID_TYPE, 0x05)


class TestErrorsReports(TestCase):
    """Test the reporting of structural errors"""
    def setUp(self):
        """Create a default set of errors"""
        self.err_a = ElementErrors(mode=MODE_AND)
        self.err_b = ElementErrors(mode=MODE_OR)

    def test_none_reported(self):
        """None Reported"""
        self.assertFalse(self.err_a)
        self.assertFalse(self.err_b)

    def test_noerrors_reported(self):
        """No Errors Reported"""
        self.err_a['one'] = NO_ERROR
        self.err_b['one'] = NO_ERROR
        self.assertFalse(self.err_a)
        self.assertFalse(self.err_b)
        self.err_a['two'] = NO_ERROR
        self.err_b['two'] = NO_ERROR
        self.assertFalse(self.err_a)
        self.assertFalse(self.err_b)

    def test_and_errors(self):
        """When Any Fail"""
        self.err_a['one'] = INVALID_TYPE
        self.assertTrue(self.err_a)
        self.err_a['two'] = NO_ERROR
        self.assertTrue(self.err_a)

    def test_remove_and_error(self):
        """When AND error removed"""
        self.err_a['one'] = INVALID_TYPE
        self.err_a['one'] = NO_ERROR
        self.assertFalse(self.err_a)

    def test_or_errors(self):
        """When All Fail"""
        self.err_b['one'] = INVALID_TYPE
        self.assertTrue(self.err_b)
        self.err_b['two'] = NO_ERROR
        self.assertFalse(self.err_b)
        self.err_b['one'] = NO_ERROR
        self.assertFalse(self.err_b)

    def test_remove_or_error(self):
        """When OR error removed"""
        self.err_b['one'] = INVALID_TYPE
        self.err_b['two'] = NO_ERROR
        self.assertFalse(self.err_b)
        self.err_b.pop('two')
        self.assertTrue(self.err_b)

    def test_error_comparison(self):
        """Test Errors Against"""
        self.err_a['one'] = INVALID_TYPE
        self.err_a['two'] = INVALID_MINLENGTH
        self.err_a['three'] = INVALID_MAXLENGTH
        self.assertEqual(self.err_a, {
            'one': INVALID_TYPE, 'two': INVALID_MINLENGTH, 'three': 0x04,
        })
        self.assertNotEqual(self.err_a, {
            'one': NO_ERROR, 'two': INVALID_MINLENGTH, 'three': INVALID_MAXLENGTH,
        })

    def test_sub_tests(self):
        """Report can contain reports"""
        self.err_a['one'] = self.err_b
        self.assertTrue(isinstance(self.err_a['one'], ElementErrors))

    def test_sub_false(self):
        """False SubReport is nonError"""
        self.err_a['one'] = NO_ERROR
        self.err_a['two'] = self.err_b
        self.err_b['one'] = NO_ERROR
        self.assertFalse(self.err_a)
        self.assertFalse(self.err_b)

    def test_sub_true(self):
        """True SubReport is Error"""
        self.err_b['one'] = INVALID_TYPE
        self.err_a['one'] = NO_ERROR
        self.err_a['two'] = self.err_b
        self.assertTrue(self.err_a)
        self.assertTrue(self.err_b)

    def test_sub_logic(self):
        """True SupReport no effect"""
        self.err_a['one'] = INVALID_TYPE
        self.err_a['two'] = self.err_b
        self.assertTrue(self.err_a)
        self.assertFalse(self.err_b)
