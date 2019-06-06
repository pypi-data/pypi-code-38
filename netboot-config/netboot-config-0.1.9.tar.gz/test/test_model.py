from assertpy import assert_that

from netboot_config.model import HostConfig


class TestHostConfig(object):

    def setup_method(self):
        self.uut = HostConfig()

    def test_renders_empty_config(self):
        result = self.uut.render()

        assert_that(result).is_none()

    def test_renders_single_entry(self):
        self.uut.add("foo", 'bar')

        result = self.uut.render()

        assert_that(result).is_equal_to('CONFIG=foo;bar;10.0.0.1;300')

    def test_renders_multiple_entrie(self):
        self.uut.add("foo", 'bar')
        self.uut.add("baz", 'qux')

        result = self.uut.render()

        assert_that(result).is_equal_to('CONFIG=foo;bar;10.0.0.1;300,baz;qux;10.0.0.1;300')
