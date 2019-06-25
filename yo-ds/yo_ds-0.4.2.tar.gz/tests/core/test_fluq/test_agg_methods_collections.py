from tests.core.common import *
import pandas as pd
import numpy as np

class ToCollectionMethodsTests(LinqTestBase):
    def test_to_dictionary_normal(self):
        d = Query.args(1,2,3).to_dictionary(lambda z: z, lambda z: str(z))
        self.assertDictEqual({1:'1',2:'2',3:'3'},d)

    def test_to_dictionary_duplicating(self):
        self.assertRaises(ValueError,lambda: Query.args(1,1,2).to_dictionary(lambda z: z, lambda z: str(z)))

    def test_to_dictionary_key_value_pair(self):
        d = Query.args(1,2,3).select(lambda z: KeyValuePair(z,str(z))).to_dictionary()
        self.assertDictEqual({1: '1', 2: '2', 3: '3'}, d)

    def test_to_dictionary_key_value_pair_override(self):
        d = Query.dict(dict(a=1,b=2)).to_dictionary(lambda z: z.key.upper(), lambda z: z.value+1)
        self.assertDictEqual(dict(A=2,B=3),d)

    def test_to_dictionary_mixture(self):
        self.assertRaises(ValueError,lambda: Query.args(KeyValuePair(1,2),1).to_dictionary())

    def test_to_dictionary_without_key_selector(self):
        self.assertRaises(ValueError, lambda: Query.args(1).to_dictionary())

    def test_to_dictionary_without_value_selector(self):
        self.assertRaises(ValueError, lambda: Query.args(1).to_dictionary(lambda z: z))

    def test_to_dictionary_grby(self):
        result = Query.args(1,2,3,4).group_by(lambda z: z%2).to_dictionary()
        self.assertDictEqual({0:[2,4],1:[1,3]},result)

    def test_to_tuple(self):
        t = Query.args(1,2,3).to_tuple()
        self.assertIsInstance(t,tuple)
        self.assertListEqual([1,2,3],list(t))

    def test_to_set_1(self):
        st = Query.args(1,2,3).to_set()
        self.assertSetEqual({1,2,3},st)

    def test_to_set_2(self):
        self.assertRaises(ValueError,lambda: Query.args(1,2,2).to_set())

    def test_to_ndarray_1d(self):
        arr = Query.args(1,2,3).to_ndarray()
        self.assertEqual(type(arr),np.ndarray)

    def test_to_ndarray_2d(self):
        arr = Query.args([1,2],[3,4]).to_ndarray()
        self.assertListEqual([2,2],list(arr.shape))
        self.assertEqual(3,arr[1,0])

    def test_to_series_default(self):
        ser = Query.args(1,2,3).to_series()
        self.assertEqual(type(ser), pd.Series)
        self.assertListEqual([1,2,3],list(ser))

    def test_to_series_value_selector(self):
        ser = Query.args(1,2,3).to_series(str)
        self.assertListEqual(['1','2','3'],list(ser))

    def test_to_series_index_selector(self):
        ser = Query.args(1,2,3).to_series(item_to_index=str)
        self.assertListEqual([1,2,3],list(ser))
        self.assertListEqual(['1','2','3'], list(ser.index))

    def test_to_series_both_selectors(self):
        ser = Query.args(1, 2, 3).to_series(lambda z: -z, str)
        self.assertListEqual([-1, -2, -3], list(ser))
        self.assertListEqual(['1', '2', '3'], list(ser.index))

    def test_to_series_key_value_pair(self):
        ser = Query.args(1,2,3).select(lambda z: KeyValuePair(z,str(z))).to_series()
        self.assertListEqual([1,2,3],list(ser.index))
        self.assertListEqual(['1','2','3'], list(ser))

    def test_to_series_special_case(self):
        ser = Query.args(1,2,3,4).group_by(lambda z: z%2).to_series(lambda z: len(z),lambda z: z.key)
        self.assertListEqual([2,2],list(ser))
        self.assertEqual([1,0],list(ser.index))

    def test_to_df(self):
        data = Query.en([1,2,3]).select_many(lambda a: Query.en(['a','b']).select(lambda b: Obj(A=a,B=b))).to_dataframe()
        self.assertListEqual(['A','B'], list(data.columns))
        self.assertEqual('int64',data.A.dtype.name)
        self.assertEqual('object',data.B.dtype.name)
        self.assertListEqual([1, 1, 2, 2, 3, 3], list(data.A))
        self.assertListEqual(['a', 'b', 'a', 'b', 'a', 'b'], list(data.B))
