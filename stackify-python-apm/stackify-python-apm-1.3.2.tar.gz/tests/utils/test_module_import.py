from unittest import TestCase

from stackifyapm.utils.module_import import import_string


class ImportStringTest(TestCase):

    def test_should_raise_exception_given_invalid_stirng(self):
        string = 'invalid-string-import'

        with self.assertRaises(ImportError) as context:
            import_string(string)

        assert context.exception.args[0] == "invalid-string-import doesn't look like a module path"

    def test_should_raise_exception_given_invalid_attribute(self):
        string = 'unittest.InvalidTestCase'

        with self.assertRaises(ImportError) as context:
            import_string(string)

        assert context.exception.args[0] == "Module 'unittest' does not define a 'InvalidTestCase' attribute/class"

    def test_should_not_raise_if_given_valid_string(self):
        string = 'unittest.TestCase'

        assert import_string(string)
