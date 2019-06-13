import unittest
from yo_core._common.obj import Obj, _EXCEPTIONS
import json

class ObjTests(unittest.TestCase):

    def test_init_and_getattr(self):
        obj = Obj(a=1)
        self.assertEqual(1,obj.a)

    def test_getattr_and_setattr(self):
        obj = Obj(a=1)
        obj.a=2
        self.assertEqual(2,obj.a)

    def test_setindex_and_getattr(self):
        obj = Obj(a=1)
        obj['a']=2
        self.assertEqual(2, obj.a)

    def test_getindex(self):
        obj = Obj(a=1)
        self.assertEqual(1,obj['a'])

    def test_reserved_fields(self):
        obj = Obj()
        for field in _EXCEPTIONS:
            self.assertRaises(ValueError,lambda: setattr(obj,field,None))

    def test_keys_values_and_items(self):
        obj = Obj(a=1,b=2,c=3,d=4,e=5,f=6)
        self.assertListEqual(list("abcdef"),list(obj.keys()))
        self.assertListEqual([1,2,3,4,5,6],list(obj.values()))
        self.assertListEqual(
            list(zip("abcdef",[1,2,3,4,5,6])),
            list(obj.items()))

    def test_update(self):
        obj = Obj(a=1,b=2)
        obj = obj.update(b=-2, c=-3)
        self.assertEqual(obj.a,1)
        self.assertEqual(obj.b,-2)
        self.assertEqual(obj.c,-3)

    def test_hasattr(self):
        obj = Obj(a=1)
        self.assertEqual(True,hasattr(obj,'a'))
        self.assertEqual(False,hasattr(obj,'b'))

    def test_remove(self):
        obj = Obj(a=1)
        obj = obj.remove('a')
        self.assertEqual(False,hasattr(obj,'a'))
        self.assertRaises(AttributeError,lambda: print(obj.a))


    def test_repr(self):
        obj = Obj(a=1,b=Obj(c=3,d=4))
        self.assertEqual("{'a': 1, 'b': {'c': 3, 'd': 4}}",obj.__repr__())

    def test_json(self):
        obj = Obj(a=1,b=Obj(c=3,d=4))
        s = json.dumps(obj)
        self.assertEqual('{"a": 1, "b": {"c": 3, "d": 4}}',s)

    def test_obj_create(self):
        obj = Obj.create({'a':[1,2],'b': {'c':1}})
        self.assertListEqual([1,2],obj.a)
        self.assertEqual(1,obj.b.c)



