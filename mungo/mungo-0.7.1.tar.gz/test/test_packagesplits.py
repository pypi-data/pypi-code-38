import unittest

from mungo.solver import split_package_constraint


class TestPackageSplitting(unittest.TestCase):

    # def test_build(self):
    #     split = split_package_constraint("pysocks 4 rc3")
    #     self.assertEqual(split, ("pysocks", [['4', 'rc3']]))
    #     # TODO what's the expected behaviour?

    def test_multisplit(self):
        split = split_package_constraint("pysocks >=1.5.6,<2.0,!=1.5.7")
        self.assertEqual(split, ("pysocks", [[">=", "1.5.6"], ["<", "2.0"], ["!=", "1.5.7"]]))

    def test_multisplit_whitespace(self):
        split = split_package_constraint("pysocks>=   1.5.6,  <  2.0,!= 1.5.7")
        self.assertEqual(split, ("pysocks", [[">=", "1.5.6"], ["<", "2.0"], ["!=", "1.5.7"]]))

    def test_unknown(self):
        split = split_package_constraint("pysocks 1=4")
        # TODO what's the expected behaviour?, assertion


if __name__ == '__main__':
    unittest.main()
