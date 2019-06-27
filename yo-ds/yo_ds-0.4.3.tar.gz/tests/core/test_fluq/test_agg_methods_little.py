from tests.core.common import *


class LittleMethodsTests(LinqTestBase):

    def test_count(self):
        self.assertEqual(3,Query.args(1,2,3).count())

    def test_first_1(self):
        self.assertEqual(1, Query.args(1, 2, 3).first())


    def test_first_2(self):
        self.assertRaises(ValueError,lambda: Query.args().first())

    def test_first_or_default_1(self):
        self.assertEqual(1, Query.args(1, 2, 3).first_or_default())


    def test_first_or_default_2(self):
        self.assertEqual(-1, Query.args().first_or_default(-1))


    def test_last_1(self):
        self.assertEqual(3, Query.args(1, 2, 3).last())


    def test_last_2(self):
        self.assertRaises(ValueError, lambda: Query.args().last())


    def test_last_or_default_1(self):
        self.assertEqual(3, Query.args(1, 2, 3).last_or_default())


    def test_last_or_default_2(self):
        self.assertEqual(-1, Query.args().last_or_default(-1))


    def test_single_1(self):
        self.assertEqual(1, Query.args(1).single())


    def test_single_2(self):
        self.assertRaises(ValueError,lambda: Query.args().last())


    def test_single_3(self):
        self.assertRaises(ValueError,lambda: Query.args(1, 2).single())


    def test_single_or_default_1(self):
        self.assertEqual(1, Query.args(1).single_or_default())


    def test_single_or_default_2(self):
        self.assertEqual(-1, Query.args().single_or_default(-1))


    def test_single_or_default_3(self):
        self.assertRaises(ValueError,lambda:Query.args(1, 2).single_or_default())


    def test_skip(self):
        self.assertQuery(Query.args(1, 2, 3, 4, 5).skip(3), 4, 5)


    def test_take(self):
        self.assertQuery(Query.args(1, 2, 3, 4, 5).take(2), 1, 2)

    def test_all_1(self):
        self.assertEqual(True, Query.args(1, 2, 3).all(lambda z: z > 0))

    def test_all_2(self):
        self.assertEqual(False, Query.args(1, 2, 3).all(lambda z: z > 1))

    def test_all_3(self):
        self.assertEqual(True, Query.args(dict()).all())

    def test_all_4(self):
        self.assertEqual(True, Query.args().all())


    def test_any_1(self):
        self.assertEqual(True, Query.args(1, 2, 3).any(lambda z: z > 1))

    def test_any_2(self):
        self.assertEqual(False, Query.args(1, 2, 3).any(lambda z: z < 1))

    def test_any_3(self):
        self.assertEqual(True, Query.args(dict()).any())

    def test_any_4(self):
        self.assertEqual(False, Query.args().any())


    def test_sum(self):
        self.assertEqual(6,Query.args(1,2,3).sum())