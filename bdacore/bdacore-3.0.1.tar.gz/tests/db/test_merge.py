import unittest

from bdacore.db.merge import merge_sql


class TestMerge(unittest.TestCase):
    def test_merge_natural_join(self):
        out = merge_sql("left", "right")

        # Check
        print(out)
        self.assertTrue(out == "select * from left left_table inner join right right_table ;")
