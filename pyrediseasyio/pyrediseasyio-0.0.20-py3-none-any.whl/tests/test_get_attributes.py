import unittest
from pyrediseasyio.io.io_group import IOGroup
from pyrediseasyio import BooleanIO, IntIO, FloatIO
from assertpy import assert_that


class TestGroup(IOGroup):
    length = 5
    Bool1 = BooleanIO("Boolean 1", "Bool1", False)
    Bool2 = BooleanIO("Boolean 2", "Bool2", True)
    Int1 = IntIO("Integer 1", "Int1")
    Int2 = IntIO("Integer 2", "Int2", default=34)
    Float1 = FloatIO("Float 1", "Float1", default=1.2)


class TestGroup2(IOGroup):
    length = 5
    Bool1 = BooleanIO("Boolean 1")
    Bool2 = BooleanIO("Boolean 2")
    Int1 = IntIO("Integer 1", "Int1")
    Int2 = IntIO("Integer 2", "Int2", default=34)
    Float1 = FloatIO("Float 1", "MyName", default=1.2)


test_group = TestGroup()
test_group2 = TestGroup2(namespace="Test")


class TestAttributes(unittest.TestCase):

    def test_get_all_attributes(self):
        attrs = test_group.get_attributes()
        assert_that(len(attrs)).is_equal_to(TestGroup.length)

    def test_limit_attributes_by_names(self):
        attrs = test_group.get_attributes(by_names=['Bool1','Float1'])
        assert_that(len(attrs)).is_equal_to(2)

    def test_limit_attributes_by_type(self):
        attrs = test_group.get_attributes(by_type=[IntIO, FloatIO])
        assert_that(len(attrs)).is_equal_to(3)

    def test_limit_by_io_filter(self):
        attrs = test_group.get_attributes(by_lambda_each=lambda x: x.value == 1.2)
        assert_that(len(attrs)).is_equal_to(1)

    def test_limit_by_io_result(self):
        attrs = test_group.get_attributes(by_lambda_results=lambda x: x[-1:])
        assert_that(len(attrs)).is_equal_to(1)
        assert_that(attrs[0].value).is_equal_to(34)

    def test_namespace(self):
        assert_that(test_group2.Bool1.key).is_equal_to(f'TestBool1')
        assert_that(test_group2.Float1.key).is_equal_to('TestMyName')

