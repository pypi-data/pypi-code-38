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


test_group = TestGroup()


def html_equals(html1, html2):
    lines1 = [l for l in diff_utils.html2list(html1) if l != '\n ' and l != ' ' and l != '\n']
    lines2 = [l for l in diff_utils.html2list(html2) if l != '\n ' and l != ' ' and l != '\n']
    return lines1 == lines2


class TestHTML(unittest.TestCase):

    def test_boolean_div_conversion(self):
        h = HMTLIOGroup(test_group, "my_id", "my_namespace").html().render()
        expected = '''
        <div class="my_namespace_io_container" id="my_id_io_container">
          <div class="my_namespace_io" id="my_id_Bool1_io">
            <div class="my_namespace_io_name">Boolean 1</div>
            <div class="my_namespace_io_value" id="my_id_Bool1_io_value" onchange="OnIOValueChange(event)">False</div>
            <div class="my_namespace_io_units">On/Off</div>
          </div>
          <div class="my_namespace_io" id="my_id_Float1_io">
            <div class="my_namespace_io_name">Float 1</div>
            <div class="my_namespace_io_value" id="my_id_Float1_io_value" onchange="OnIOValueChange(event)">1.23</div>
            <div class="my_namespace_io_units">furlongs</div>
          </div>
        </div>
        '''
        assert_that(html_equals(h, expected)).is_true()

    def test_boolean_table_conversion(self):
        h = HMTLIOGroup(test_group, "my_id", "my_namespace").html_table().render()
        expected = '''
        <table class="my_namespace_io_container" id="my_id_io_container">
          <tr class="my_namespace_io" id="my_id_Bool1_io">
            <td class="my_namespace_io_name">Boolean 1</td>
            <td class="my_namespace_io_value" id="my_id_Bool1_io_value" onchange="OnIOValueChange(event)">False</td>
            <td class="my_namespace_io_units">On/Off</td>
          </tr>
          <tr class="my_namespace_io" id="my_id_Float1_io">
            <td class="my_namespace_io_name">Float 1</td>
            <td class="my_namespace_io_value" id="my_id_Float1_io_value" onchange="OnIOValueChange(event)">1.23</td>
            <td class="my_namespace_io_units">furlongs</td>
          </tr>
        </table>
        '''
        assert_that(html_equals(h, expected)).is_true()

    def test_json_dumps_basic(self):
        h = HMTLIOGroup(test_group, "my_id", "my_namespace")
        d = h.dumps()
        as_list = json.loads(d)
        assert_that(len(as_list)).is_equal_to(len(test_group))
        assert_that(as_list[0]['name']).is_equal_to('Boolean 1')

    def test_json_dumps_by_name(self):
        h = HMTLIOGroup(test_group, "my_id", "my_namespace")
        d = h.dumps(by_names=['Bool1'])
        as_list = json.loads(d)
        assert_that(len(as_list)).is_equal_to(1)
