from unittest import TestCase
from jkl_serialization import deserialize_jkl, serialize_jkl


class Test_jkl_serialization(TestCase):
    string = """3
0 4
-2.772589 2 1 2
-2.865831 0
-2.963209 1 2
-2.963209 1 1
1 4
-2.772589 2 0 2
-2.865831 0
-2.963209 1 2
-2.963209 1 0
2 4
-2.772589 2 0 1
-2.865831 0
-2.963209 1 1
-2.963209 1 0
"""

    obj = {'0': [('-2.772589', ['1', '2']),
                 ('-2.865831', []),
                 ('-2.963209', ['2']),
                 ('-2.963209', ['1'])],
           '1': [('-2.772589', ['0', '2']),
                 ('-2.865831', []),
                 ('-2.963209', ['2']),
                 ('-2.963209', ['0'])],
           '2': [('-2.772589', ['0', '1']),
                 ('-2.865831', []),
                 ('-2.963209', ['1']),
                 ('-2.963209', ['0'])]}

    def test_deserialize_jkl(self):
        self.assertEqual(self.obj, deserialize_jkl(self.string))

    def test_serialize_jkl(self):
        self.assertEqual(self.string, serialize_jkl(self.obj))
