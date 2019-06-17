import unittest

from pyrediseasyio.io_group import IOGroup
from pyrediseasyio.single_io import BooleanIO, IntIO, FloatIO
from assertpy import assert_that


class TestGroup(IOGroup):
    Bool1 = BooleanIO("Boolean 1", "Bool1", False)
    Bool2 = BooleanIO("Boolean 2", "Bool2", True)
    Int1 = IntIO("Integer 1", "Int1")
    Int2 = IntIO("Integer 2", "Int2", default=34)
    Float1 = FloatIO("Float 1", "Float1", default=1.2)


class TestGroup2(IOGroup):
    Bool1 = BooleanIO("Boolean 1", "Bool1", False)
    Bool2 = BooleanIO("Boolean 2", "Bool2", True)
    Int1 = IntIO("Integer 1", "Int1")
    Int2 = IntIO("Integer 2", "Int2", default=34)
    Float1 = FloatIO("Float 1", "Float1", default=1.2)


class TestGroup3(IOGroup):
    def __init__(self, db=2):
        self.Bool1 = BooleanIO("Boolean 1", "Bool1", False)
        self.Bool2 = BooleanIO("Boolean 2", "Bool2", True)
        self.Int1 = IntIO("Integer 1", "Int1")
        self.Int2 = IntIO("Integer 2", "Int2", default=34)
        self.Float1 = FloatIO("Float 1", "Float1", default=1.2)
        super().__init__(db=db)


class TestReadWrite(unittest.TestCase):

    def setUp(self):
        self.group = TestGroup()
        self.group2 = TestGroup2()
        self.group3 = TestGroup3()

    def test_that_defaults_are_applied(self):
        group = self.group
        group3 = self.group3

        assert_that(group.Bool1).is_false()
        assert_that(group.Bool2).is_true()
        assert_that(group.Int1).is_equal_to(0)
        assert_that(group.Int2).is_equal_to(34)
        assert_that(group.Float1).is_equal_to(1.2)

        assert_that(group3.Bool1).is_false()
        assert_that(group3.Bool2).is_true()
        assert_that(group3.Int1).is_equal_to(0)
        assert_that(group3.Int2).is_equal_to(34)
        assert_that(group3.Float1).is_equal_to(1.2)

    def test_basic_read_write(self):
        group1 = self.group
        group2 = self.group2

        group4 = TestGroup3(db=2)
        group5 = TestGroup3(db=2)

        group1.Bool1 = True
        assert_that(group2.Bool1).is_true()
        group1.Bool1 = False
        assert_that(group2.Bool1).is_false()

        group1.Int1 = 100
        assert_that(group2.Int1).is_equal_to(100)
        group1.Int1 = -100
        assert_that(group2.Int1).is_equal_to(-100)

        group4.Float1 = 123.4
        assert_that(group5.Float1).is_equal_to(123.4)

        group4.Bool1 = True
        assert_that(group5.Bool1).is_true()
        group4.Bool1 = False
        assert_that(group5.Bool1).is_false()

        group4.Int1 = 100
        assert_that(group5.Int1).is_equal_to(100)
        group4.Int1 = -100
        assert_that(group5.Int1).is_equal_to(-100)

        group4.Float1 = 123.4
        assert_that(group5.Float1).is_equal_to(123.4)

    def test_same_name_different_database(self):
        group1 = self.group
        group2 = self.group2
        group3 = self.group3
        group4 = TestGroup3(db=5)

        group1.Int1 = 234
        assert_that(group2.Int1).is_equal_to(234)
        assert_that(group3.Int1).is_not_equal_to(234)

        group4.Float1 = 555
        assert_that(group4.Float1).is_equal_to(555)
        assert_that(group3.Float1).is_not_equal_to(555)

    def test_that_group_can_be_saved_to_memory(self):
        group = self.group
        group2 = self.group2
        j = group.dump("SomeKey")
        assert_that(j).is_not_none()
        assert_that(len(j)).is_greater_than(10)

        r = group2.read("SomeKey")
        assert_that(r).is_equal_to(j)

    def test_arithmatic_operations(self):
        group1 = self.group
        group3 = self.group3

        group1.Float1 = 10.0
        group3.Float1 = 20.0

        assert_that(group1.Float1 + group3.Float1).is_equal_to(30)
        assert_that(group1.Float1 * group3.Float1).is_equal_to(200)
        assert_that(group3.Float1 / group1.Float1).is_equal_to(2)
        assert_that(group3.Float1 - group1.Float1).is_equal_to(10)


