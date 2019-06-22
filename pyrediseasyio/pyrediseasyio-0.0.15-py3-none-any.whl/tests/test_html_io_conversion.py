import unittest
from pyrediseasyio.io.io_group import IOGroup
from pyrediseasyio.html.html_io import HTMLIO
from pyrediseasyio import BooleanIO, SingleIO, FloatIO, StringIO
from assertpy import assert_that
from htmldiffer import utils as diff_utils


class TestGroup(IOGroup):
    Bool1 = BooleanIO("Boolean 1", "Bool1", units="On/Off")
    Float1 = FloatIO("Float 1", "Float1", default=1.23, units="furlongs")


test_group = TestGroup()


def html_equals(html1, html2):
    lines1 = [l for l in diff_utils.html2list(html1) if l != '\n ' and l != ' ' and l != '\n']
    lines2 = [l for l in diff_utils.html2list(html2) if l != '\n ' and l != ' ' and l != '\n']
    return lines1 == lines2


class TestHTML(unittest.TestCase):

    def test_boolean_div_conversion(self):
        h = HTMLIO(test_group.Bool1, html_id_header="my_id", namespace="my_ns").html().render()
        expected = '''
        <div class="my_ns_io" id="my_id_Bool1_io">
          <div class="my_ns_io_name">Boolean 1</div>
          <div class="my_ns_io_value" id="my_id_Bool1_io_value" onchange="OnIOValueChange(event)">False</div>
          <div class="my_ns_io_units">On/Off</div>
        </div>
        '''
        assert_that(html_equals(h, expected)).is_true()

    def test_bool_row_conversion(self):
        h = HTMLIO(test_group.Bool1, html_id_header="my_id", namespace="my_ns").html_row().render()
        expected = '''
        <tr class="my_ns_io" id="my_id_Bool1_io">
          <td class="my_ns_io_name">Boolean 1</td>
          <td class="my_ns_io_value" id="my_id_Bool1_io_value" onchange="OnIOValueChange(event)">False</td>
          <td class="my_ns_io_units">On/Off</td>
        </tr>
        '''
        assert_that(html_equals(h, expected)).is_true()

    def test_float_div_conversion(self):
        h = HTMLIO(test_group.Float1, html_id_header="my_id", namespace="my_ns").html().render()
        print(h)
        expected = '''
        <div class="my_ns_io" id="my_id_Float1_io">
          <div class="my_ns_io_name">Float 1</div>
          <div class="my_ns_io_value" id="my_id_Float1_io_value" onchange="OnIOValueChange(event)">1.23</div>
          <div class="my_ns_io_units">furlongs</div>
        </div>
        '''
        assert_that(html_equals(h, expected)).is_true()

