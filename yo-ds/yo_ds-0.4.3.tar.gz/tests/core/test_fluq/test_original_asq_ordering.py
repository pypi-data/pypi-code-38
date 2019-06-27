from tests.core.common import *

class OrderingTests(LinqTestBase):

    def test_order_by(self):
        self.assertQuery(Query.args('ccc', 'bb', 'a').order_by(len), 'a', 'bb', 'ccc')


    def test_order_by_descending(self):
        self.assertQuery(Query.args('ccc', 'bb', 'a').order_by_descending(len), 'ccc', 'bb', 'a')

    def test_order_then_1(self):
        self.assertQuery(Query.args('a2', 'b1', 'b2', 'a1').order_by(lambda z: z[0]).then_by(lambda z: z[1]), 'a1',
                   'a2', 'b1', 'b2')

    def test_order_then_2(self):
        self.assertQuery(
            Query.args('a2', 'b1', 'b2', 'a1').order_by(lambda z: z[0]).then_by_descending(lambda z: z[1]),
            'a2', 'a1', 'b2', 'b1')

    def test_order_then_3(self):
        self.assertQuery(
            Query.args('a2', 'b1', 'b2', 'a1').order_by_descending(lambda z: z[0]).then_by(lambda z: z[1]),
            'b1', 'b2', 'a1', 'a2')

    def test_order_then_4(self):
        self.assertQuery(
            Query.args('a2', 'b1', 'b2', 'a1').order_by_descending(lambda z: z[0]).then_by_descending(lambda z: z[1]),
            'b2', 'b1', 'a2', 'a1')

    def test_then(self):
        self.assertRaises(ValueError, lambda: Query.args(1, 2).then_by(lambda z: z).to_list())

    def test_then_desc(self):
        self.assertRaises(ValueError, lambda: Query.args(1, 2).then_by_descending(lambda z: z).to_list())

