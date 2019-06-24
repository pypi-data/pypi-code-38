import unittest
from pyrediseasyio.io.io_group import IOGroup
from pyrediseasyio.html.html_io_group import HMTLIOGroup
from pyrediseasyio import BooleanIO, SingleIO, FloatIO, StringIO
from assertpy import assert_that
from htmldiffer import utils as diff_utils
import json


class TestGroup(IOGroup):
    Bool1 = BooleanIO("Boolean 1", units="On/Off")
    Float1 = FloatIO("Float 1", default=1.23, units="furlongs")


test_group = TestGroup(namespace='Pin1')


def html_equals(html1, html2):
    lines1 = [l for l in diff_utils.html2list(html1) if l != '\n ' and l != ' ' and l != '\n']
    lines2 = [l for l in diff_utils.html2list(html2) if l != '\n ' and l != ' ' and l != '\n']
    return lines1 == lines2


class TestHTML(unittest.TestCase):

    def test_boolean_div_conversion(self):
        h = HMTLIOGroup(test_group).html().render()
        print(h)
        expected = '''
        <div class="easyio_io_container" id="Pin1Bool1_io_container">
          <div class="easyio_io" id="Pin1Bool1_io">
            <div class="easyio_name">Boolean 1</div>
            <div class="easyio_value" data-addr="Bool1" data-namespace="Pin1" id="Pin1Bool1" onchange="OnIOValueChange(event)">False</div>
            <div class="easyio_units">On/Off</div>
          </div>
          <div class="easyio_io" id="Pin1Float1_io">
            <div class="easyio_name">Float 1</div>
            <div class="easyio_value" data-addr="Float1" data-namespace="Pin1" id="Pin1Float1" onchange="OnIOValueChange(event)">1.23</div>
            <div class="easyio_units">furlongs</div>
          </div>
        </div>
        '''
        assert_that(html_equals(h, expected)).is_true()

    def test_boolean_table_conversion(self):
        h = HMTLIOGroup(test_group).html_table().render()
        expected = '''
        <table class="Pin1_io_container" id="Bool1_io_container">
          <tr class="easyio_io" id="Pin1Bool1_io">
            <td class="easyio_name">Boolean 1</td>
            <td class="easyio_value" data-addr="Bool1" data-namespace="Pin1" id="Pin1Bool1" onchange="OnIOValueChange(event)">False</td>
            <td class="easyio_units">On/Off</td>
          </tr>
          <tr class="easyio_io" id="Pin1Float1_io">
            <td class="easyio_name">Float 1</td>
            <td class="easyio_value" data-addr="Float1" data-namespace="Pin1" id="Pin1Float1" onchange="OnIOValueChange(event)">1.23</td>
            <td class="easyio_units">furlongs</td>
          </tr>
        </table>
        '''
        assert_that(html_equals(h, expected)).is_true()

    def test_different_id(self):
        h = HMTLIOGroup(test_group, html_id="NewID").html_table().render()
        expected = '''
        <table class="Pin1_io_container" id="NewID">
          <tr class="easyio_io" id="Pin1Bool1_io">
            <td class="easyio_name">Boolean 1</td>
            <td class="easyio_value" id="Pin1Bool1" onchange="OnIOValueChange(event)">False</td>
            <td class="easyio_units">On/Off</td>
          </tr>
          <tr class="easyio_io" id="Pin1Float1_io">
            <td class="easyio_name">Float 1</td>
            <td class="easyio_value" id="Pin1Float1" onchange="OnIOValueChange(event)">1.23</td>
            <td class="easyio_units">furlongs</td>
          </tr>
        </table>
        '''
        assert_that(html_equals(h, expected)).is_true()

    def test_json_dumps_basic(self):
        h = HMTLIOGroup(test_group)
        d = h.dumps()
        as_list = json.loads(d)
        assert_that(len(as_list)).is_equal_to(len(test_group))
        assert_that(as_list[0]['name']).is_equal_to('Boolean 1')


    def test_json_dumps_by_name(self):
        h = HMTLIOGroup(test_group, "new_ns")
        d = h.dumps(by_names=['Bool1'])
        print(d)
        as_list = json.loads(d)
        assert_that(len(as_list)).is_equal_to(1)
