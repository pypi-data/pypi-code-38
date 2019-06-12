import unittest
from unittest.mock import MagicMock
from controlpyweb.single_io import SingleIO, DiscreteIn
from assertpy import assert_that


class Container:
    single_io1 = SingleIO(name="SIO1", addr="0.1", default="Hello", reader=MagicMock())
    single_io2 = SingleIO(name="SIO2", addr="0.2", default="Hello", reader=MagicMock())
    discrete_in_1 = DiscreteIn(name="DiscreteIn1", addr="0.2", default=False, reader=MagicMock())


class TestSingleIO(unittest.TestCase):

    def setUp(self):
        self.container = Container()
        self.reader1_read_method = MagicMock()
        self.reader2_read_method = MagicMock()
        self.reader_read_immediate_method = MagicMock()
        self.container.single_io1._reader_writer.read = self.reader1_read_method
        self.container.single_io1._reader_writer.read_immediate = self.reader_read_immediate_method
        self.container.single_io2._reader_writer.read = self.reader2_read_method
        self.container.single_io2._reader_writer.read_immediate = self.reader_read_immediate_method

    def test_get_set(self):
        container = self.container
        self.reader1_read_method.return_value = "World"
        self.container.single_io1.read()
        assert_that(container.single_io1).is_equal_to("World")

    def test_immediate_read(self):
        container = self.container
        self.reader_read_immediate_method.return_value = "New"
        assert_that(container.single_io1.read_immediate()).is_equal_to("New")

    def test_equality(self):
        container = self.container
        self.reader1_read_method.return_value = "Hello"
        self.reader2_read_method.return_value = "Hello"
        container.single_io1.read()
        container.single_io2.read()
        assert_that(container.single_io1 == container.single_io1).is_true()
        assert_that(container.single_io1).is_equal_to(container.single_io2)
        self.reader1_read_method.return_value = "World"
        assert_that(container.single_io2 != container.single_io1).is_true()
        assert_that(container.single_io1).is_not_equal_to(container.single_io2)


