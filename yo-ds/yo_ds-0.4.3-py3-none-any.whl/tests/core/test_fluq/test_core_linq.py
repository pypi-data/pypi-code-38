from tests.core.common import *


class GeneralSelectorsTests(LinqTestBase):

    def test_select(self):
        self.assertQuery(Query.args(1, 2).select(str), '1', '2')

    def test_select_many(self):
        self.assertQuery(Query.args(1, 2, 3).select_many(lambda z: range(z)), 0, 0, 1, 0, 1, 2)

    def test_distinct(self):
        self.assertQuery(Query.args(1, 2, 2, 3, 3).distinct(), 1, 2, 3)

    def test_distinct_1(self):
        self.assertQuery(Query.args('aa', 'ab', 'b').distinct(lambda z: z[0]), 'aa', 'b')

    def test_where(self):
        self.assertQuery(Query.args(1, 2, 3, 4).where(lambda z: z % 2 == 0), 2, 4)

    def test_group_by(self):
        result = Query.args(2, 3, 1, 4).group_by(lambda z: z % 2).to_list()
        self.assertEqual(0, result[0].key)
        self.assertListEqual([2, 4], result[0].value)
        self.assertEqual(1, result[1].key)
        self.assertListEqual([3, 1], result[1].value)

    def test_group_by_1(self):
        result = Query.args(2,3,1,4).group_by(lambda z: z%2).select(lambda z: (z.key,Query.en(z).sum())).to_list()
        self.assertListEqual(
            [(0,6),(1,4)],
            result)

    def test_group_by_2(self):
        result = Query.args(2,3,1,4).group_by(lambda z: z%2).to_dictionary()
        self.assertDictEqual({0:[2,4],1:[3,1]},result)

    def test_aggrerate(self):
        self.assertEqual('123', Query.args('1', '2', '3').aggregate(lambda acc, el: acc + el))

    def test_cast_1(self):
        self.assertRaises(TypeError,lambda: Query.args(1,2,"3").cast(int).to_list())

    def test_cast_2(self):
        self.assertQuery(Query.args(1, 2, 3).cast(int), 1, 2, 3)

    def test_of_type(self):
        self.assertQuery(
            Query.args(1,"2",3,"4",5).of_type(int),
            1,3,5)

    def test_concat(self):
        self.assertQuery(
            Query.args(1,2,3).concat([3,4,5]),
            1,2,3,3,4,5
        )

    def test_intersect(self):
        self.assertQuery(
            Query.args(1,2,3).intersect([2,3,4]),
            2,3
        )

