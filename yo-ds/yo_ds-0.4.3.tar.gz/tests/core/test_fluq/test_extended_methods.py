from tests.core.common import *

class ExtendedMethodsTests(LinqTestBase):
    def test_argmax_1(self):
        self.assertEqual(-1, Query.args(-1, 0, 1).argmax(lambda z: abs(z)))

    def test_argmax_2(self):
        self.assertRaises(ValueError,lambda: Query.args().argmax(lambda z: abs(z)))

    def test_argmax_or_default_1(self):
        self.assertEqual(-1, Query.args(-1, 0, 1).argmax_or_default(lambda z: abs(z)))

    def test_argmax_or_default_2(self):
        self.assertEqual(-10, Query.args().argmax_or_default(lambda z: abs(z), -10))

    def test_argmin_1(self):
        self.assertEqual(0, Query.args(-1, 0, 1).argmin(lambda z: abs(z)))

    def test_argmin_2(self):
        self.assertRaises(ValueError,lambda: Query.args().argmin(lambda z: abs(z)))


    def test_argmin_or_default_1(self):
        self.assertEqual(0, Query.args(-1, 0, 1).argmin_or_default(lambda z: abs(z)))

    def test_argmin_or_default_2(self):
        self.assertEqual(-10, Query.args().argmin_or_default(lambda z: abs(z), -10))

    def test_foreach(self):
        buf = []
        Query.args(1, 2, 3).foreach(buf.append)
        self.assertListEqual([1,2,3],buf)

    def test_foreach_and_continue(self):
        buf = []
        Query.args(1, 2, 3).foreach_and_continue(lambda z: buf.append(z + 10)).foreach(buf.append)
        self.assertListEqual([11,1,12,2,13,3], buf)

    def test_append(self):
        self.assertQuery(Query.args(1, 2).append(5, 6), 1, 2, 5, 6)

    def test_prepend(self):
        self.assertQuery(Query.args(1, 2).prepend(5, 6), 5, 6, 1, 2)