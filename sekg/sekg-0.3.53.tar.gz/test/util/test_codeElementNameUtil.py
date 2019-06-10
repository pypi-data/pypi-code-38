from unittest import TestCase

from sekg.util.code import CodeElementNameUtil


class TestCodeElementNameUtil(TestCase):
    def test_uncamelize(self):
        util = CodeElementNameUtil()
        name_list = [
            ("java.util.List", "java.util. List"),
            ("java.util.ArrayList", "java.util. Array List"),
            ("ArrayList", "Array List"),
            ("FPath1", "F Path1"),
            ("FilePath1", "File Path1"),

        ]
        for name, right_name in name_list:
            self.assertEqual(right_name, util.uncamelize(name))

    def test_uncamelize_by_stemming(self):
        util = CodeElementNameUtil()
        name_list = [
            ("java.util.List", "java.util. List"),
            ("java.util.ArrayList", "java.util. Array List"),
            ("ArrayList", "Array List"),
            ("FPath1", "F Path1"),
            ("FilePath1", "File Path1"),

        ]
        for name, right_name in name_list:
            self.assertEqual(right_name, util.uncamelize_by_stemming(name))
    def test_uncamelize_from_simple_name(self):
        util = CodeElementNameUtil()
        name_list = [
            ("java.util.List", "List"),
            ("java.util.ArrayList", "Array List"),
            ("ArrayList", "Array List"),
            ("FPath1", "F Path1"),
            ("FilePath1", "File Path1"),

        ]
        for name, right_name in name_list:
            self.assertEqual(right_name, util.uncamelize_from_simple_name(name))