from tests.core.common import *


def _lazy():
    for i in range(10):
        yield i

class InitiatorsTest(LinqTestBase):
    def assertKeyValuePair(self, keys, values, results):
        for key, value, result in zip(keys,values,results):
            self.assertIsInstance(result,KeyValuePair)
            self.assertEqual(key,result.key)
            self.assertEqual(value,result.value)

    def test_sized_en(self):
        self.assertEqual(3,Query.en([1,2,3]).length)

    def test_unsized_en(self):
        self.assertEqual(None,Query.en(_lazy()).length)

    def test_unsized_count(self):
        self.assertEqual(10,Query.en(_lazy()).count())

    def test_sized_select(self):
        self.assertEqual(3,Query.args(1,2,3).select(str).length)

    def test_size_args(self):
        self.assertEqual(3,Query.args(1,2,3).length)


    def test_dict(self):
        self.assertKeyValuePair(
            ['a','b','c'],
            [1,2,3],
            Query.dict(Obj(a=1,b=2,c=3))
        )

    def test_series(self):
        self.assertKeyValuePair(
            ['a','b','c'],
            [1,2,3],
            Query.series(pd.Series([1,2,3],['a','b','c']))

        )

    def test_df(self):
        df = pd.DataFrame(columns=dict(testA=[1,2,3], testB=['1','2','3']))
        result = Query.df(df).with_indices().all(lambda z:
            z.item.testA == z.index and
            z.item.testB == str(z.index) and
            isinstance(z,Obj))
        self.assertTrue(result)
