import unittest
from abc import ABCMeta, abstractproperty


class MyABC(metaclass=ABCMeta):
    @abstractproperty
    def propA(self):
        pass


class MyMixin(metaclass=ABCMeta):
    @abstractproperty
    def propB(self):
        pass


class MyClassNoPropA(MyABC, MyMixin):
    @property
    def propB(self):
        return "b"


class MyClassNoPropB(MyABC, MyMixin):
    @property
    def propA(self):
        return "a"

class MyClass(MyABC, MyMixin):

    @property
    def propA(self):
        return "a"

    @property
    def propB(self):
        return "b"

class PluginServerEntryHookInheritenceTest(unittest.TestCase):
    def testPropANotImplemeneted(self):
        self.assertRaises(TypeError, lambda : MyClassNoPropA())

    def testPropBNotImplemeneted(self):
        self.assertRaises(TypeError, lambda : MyClassNoPropB())

    def testIsInstance(self):
        myClass = MyClass()
        self.assertTrue(isinstance(myClass, MyABC))
        self.assertTrue(isinstance(myClass, MyMixin))
