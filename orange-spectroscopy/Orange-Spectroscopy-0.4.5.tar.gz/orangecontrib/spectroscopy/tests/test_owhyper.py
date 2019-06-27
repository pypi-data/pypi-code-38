import os
import unittest
from unittest.mock import patch

import numpy as np

from AnyQt.QtCore import QPointF, Qt
import Orange
from Orange.widgets.tests.base import WidgetTest

from orangecontrib.spectroscopy.widgets.owhyper import \
    OWHyper, ANNOTATED_DATA_SIGNAL_NAME
from orangecontrib.spectroscopy.preprocess import Interpolate
from orangecontrib.spectroscopy.widgets.line_geometry import in_polygon, is_left
from orangecontrib.spectroscopy.tests.util import hold_modifiers, set_png_graph_save
from orangecontrib.spectroscopy.utils import values_to_linspace, \
    index_values, location_values, index_values_nan

NAN = float("nan")


class TestReadCoordinates(unittest.TestCase):

    def test_linspace(self):
        v = values_to_linspace(np.array([1, 2, 3]))
        np.testing.assert_equal(np.linspace(*v), [1, 2, 3])
        v = values_to_linspace(np.array([1, 2, 3, np.nan]))
        np.testing.assert_equal(np.linspace(*v), [1, 2, 3])
        v = values_to_linspace(np.array([1]))
        np.testing.assert_equal(np.linspace(*v), [1])
        v = values_to_linspace(np.array([1.001, 2, 3.002]))
        np.testing.assert_equal(np.linspace(*v), [1.001, 2.0015, 3.002])

    def test_index(self):
        a = np.array([1, 2, 3])
        v = values_to_linspace(a)
        iv = index_values(a, v)
        np.testing.assert_equal(iv, [0, 1, 2])
        a = np.array([1, 2, 3, 4])
        v = values_to_linspace(a)
        iv = index_values(a, v)
        np.testing.assert_equal(iv, [0, 1, 2, 3])
        a = np.array([1, 2, 3, 6, 5])
        v = values_to_linspace(a)
        iv = index_values(a, v)
        np.testing.assert_equal(iv, [0, 1, 2, 5, 4])

    def test_index_nan(self):
        a = np.array([1, 2, 3, np.nan])
        v = values_to_linspace(a)
        iv, nans = index_values_nan(a, v)
        np.testing.assert_equal(iv[:-1], [0, 1, 2])
        np.testing.assert_equal(nans, [0, 0, 0, 1])

    def test_location(self):
        lsc = values_to_linspace(np.array([1, 1, 1]))  # a constant
        lv = location_values([0, 1, 2], lsc)
        np.testing.assert_equal(lv, [-1, 0, 1])


class TestPolygonSelection(unittest.TestCase):

    def test_is_left(self):
        self.assertGreater(is_left(0, 0, 0, 1, -1, 0), 0)
        self.assertLess(is_left(0, 0, 0, -1, -1, 0), 0)

    def test_point(self):
        poly = [(0, 1), (1, 0), (2, 1), (3, 0), (3, 2), (0, 1)]  # non-convex

        self.assertFalse(in_polygon([0, 0], poly))
        self.assertTrue(in_polygon([1, 1.1], poly))
        self.assertTrue(in_polygon([1, 1], poly))
        self.assertTrue(in_polygon([1, 0.5], poly))
        self.assertFalse(in_polygon([2, 0], poly))
        self.assertFalse(in_polygon([0, 2], poly))

        # multiple points at once
        np.testing.assert_equal([False, True], in_polygon([[0, 0], [1, 1]], poly))

    def test_order(self):
        poly = [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]  # square
        self.assertTrue(in_polygon([0.5, 0.5], poly))
        self.assertTrue(in_polygon([0.5, 0.5], list(reversed(poly))))


class TestOWHyper(WidgetTest):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.iris = Orange.data.Table("iris")
        cls.whitelight = Orange.data.Table("whitelight.gsf")
        cls.whitelight_unknown = cls.whitelight.copy()
        cls.whitelight_unknown[0]["value"] = NAN
        # dataset with a single attribute
        cls.iris1 = Orange.data.Table(Orange.data.Domain(cls.iris.domain[:1]), cls.iris)
        # dataset without any attributes
        iris0 = Orange.data.Table(Orange.data.Domain([]), cls.iris)
        # dataset without rows
        empty = Orange.data.Table(cls.iris[:0], cls.iris)
        # dataset with large blank regions
        irisunknown = Interpolate(np.arange(20))(cls.iris)
        # dataset without any attributes, but XY
        whitelight0 = Orange.data.Table(
            Orange.data.Domain([], None, metas=cls.whitelight.domain.metas), cls.whitelight)
        cls.strange_data = [None, cls.iris1, iris0, empty, irisunknown, whitelight0]

    def setUp(self):
        self.widget = self.create_widget(OWHyper)

    def try_big_selection(self):
        self.widget.imageplot.select_square(QPointF(-100, -100), QPointF(100, 100), False)
        self.widget.imageplot.make_selection(None, False)
        self.widget.imageplot.make_selection(None, True)

    def test_strange(self):
        for data in self.strange_data:
            self.send_signal("Data", data)
            self.try_big_selection()

    def test_context_not_open_invalid(self):
        self.send_signal("Data", self.iris1)
        self.assertIsNone(self.widget.imageplot.attr_x)
        self.send_signal("Data", self.iris)
        self.assertIsNotNone(self.widget.imageplot.attr_x)

    def test_no_samples(self):
        self.send_signal("Data", self.whitelight[:0])
        self.try_big_selection()

    def test_few_samples(self):
        self.send_signal("Data", self.whitelight[:1])
        self.send_signal("Data", self.whitelight[:2])
        self.send_signal("Data", self.whitelight[:3])
        self.try_big_selection()

    def test_simple(self):
        self.send_signal("Data", self.whitelight)
        self.send_signal("Data", None)
        self.try_big_selection()
        self.assertIsNone(self.get_output("Selection"), None)

    def test_unknown(self):
        self.send_signal("Data", self.whitelight)
        levels = self.widget.imageplot.img.levels
        self.send_signal("Data", self.whitelight_unknown)
        levelsu = self.widget.imageplot.img.levels
        np.testing.assert_equal(levelsu, levels)

    def test_select_all(self):
        self.send_signal("Data", self.whitelight)

        out = self.get_output("Selection")
        self.assertIsNone(out, None)

        # select all
        self.widget.imageplot.select_square(QPointF(-100, -100), QPointF(1000, 1000), False)
        out = self.get_output("Selection")
        self.assertEqual(len(self.whitelight), len(out))

        # test if mixing increasing and decreasing works
        self.widget.imageplot.select_square(QPointF(1000, -100), QPointF(-100, 1000), False)
        out = self.get_output("Selection")
        self.assertEqual(len(self.whitelight), len(out))

        # deselect
        self.widget.imageplot.select_square(QPointF(-100, -100), QPointF(-100, -100), False)
        out = self.get_output("Selection")
        self.assertIsNone(out, None)

        # select specific points
        self.widget.imageplot.select_square(QPointF(9.4, 9.4), QPointF(11.6, 10.6), False)
        out = self.get_output("Selection")
        np.testing.assert_equal(out.metas, [[10, 10], [11, 10]])

    def test_select_polygon_as_rectangle(self):
        # rectangle and a polygon need to give the same results
        self.send_signal("Data", self.whitelight)
        self.widget.imageplot.select_square(QPointF(5, 5), QPointF(15, 10), False)
        out = self.get_output("Selection")
        self.widget.imageplot.select_polygon([QPointF(5, 5), QPointF(15, 5), QPointF(15, 10),
                                              QPointF(5, 10), QPointF(5, 5)], False)
        outpoly = self.get_output("Selection")
        self.assertEqual(list(out), list(outpoly))

    def test_select_click(self):
        self.send_signal("Data", self.whitelight)
        self.widget.imageplot.select_by_click(QPointF(1, 2), False)
        out = self.get_output("Selection")
        np.testing.assert_equal(out.metas, [[1, 2]])

    def test_select_click_multiple_groups(self):
        data = self.whitelight
        self.send_signal("Data", data)
        self.widget.imageplot.select_by_click(QPointF(1, 2), False)
        with hold_modifiers(self.widget, Qt.ControlModifier):
            self.widget.imageplot.select_by_click(QPointF(2, 2), False)
        with hold_modifiers(self.widget, Qt.ShiftModifier):
            self.widget.imageplot.select_by_click(QPointF(3, 2), False)
        with hold_modifiers(self.widget, Qt.ShiftModifier | Qt.ControlModifier):
            self.widget.imageplot.select_by_click(QPointF(4, 2), False)
        out = self.get_output(ANNOTATED_DATA_SIGNAL_NAME)
        self.assertEqual(len(out), 20000)  # have a data table at the output
        newvars = out.domain.variables + out.domain.metas
        oldvars = data.domain.variables + data.domain.metas
        group_at = [a for a in newvars if a not in oldvars][0]
        unselected = group_at.to_val("Unselected")
        out = out[np.flatnonzero(out.transform(Orange.data.Domain([group_at])).X != unselected)]
        self.assertEqual(len(out), 4)
        np.testing.assert_equal([o["x"].value for o in out], [1, 2, 3, 4])
        np.testing.assert_equal([o[group_at].value for o in out], ["G1", "G2", "G3", "G3"])

        # remove one element
        with hold_modifiers(self.widget, Qt.AltModifier):
            self.widget.imageplot.select_by_click(QPointF(1, 2), False)
        out = self.get_output("Selection")
        np.testing.assert_equal(len(out), 3)

    def test_select_a_curve(self):
        self.send_signal("Data", self.iris)
        self.widget.curveplot.make_selection([0], False)

    def test_settings_curves(self):
        self.send_signal("Data", self.iris)
        self.widget.curveplot.feature_color = "iris"
        self.send_signal("Data", self.whitelight)
        self.assertEqual(self.widget.curveplot.feature_color, None)
        self.send_signal("Data", self.iris)
        self.assertEqual(self.widget.curveplot.feature_color, "iris")

    def test_set_variable_color(self):
        data = Orange.data.Table("iris.tab")
        ndom = Orange.data.Domain(data.domain.attributes[:-1], data.domain.class_var,
                                  metas=[data.domain.attributes[-1]])
        data = data.transform(ndom)
        self.send_signal("Data", data)
        self.widget.controls.value_type.buttons[1].click()
        with patch("orangecontrib.spectroscopy.widgets.owhyper.ImageItemNan.setLookupTable") as p:
            self.widget.attr_value = "iris"
            self.widget.imageplot.update_color_schema()
            np.testing.assert_equal(len(p.call_args[0][0]), 3)  # just 3 colors for 3 values
            self.widget.attr_value = "petal width"
            self.widget.imageplot.update_color_schema()
            np.testing.assert_equal(len(p.call_args[0][0]), 256)  # 256 for a continuous variable

    def test_single_update_view(self):
        with patch("orangecontrib.spectroscopy.widgets.owhyper.ImagePlot.update_view") as p:
            self.send_signal("Data", self.iris)
            self.assertEqual(p.call_count, 1)

    def test_migrate_selection(self):
        c = QPointF()  # some we set an attribute to
        setattr(c, "selection", [False, True, True, False])
        settings = {"context_settings": [c]}
        OWHyper.migrate_settings(settings, 2)
        self.assertEqual(settings["imageplot"]["selection_group_saved"], [(1, 1), (2, 1)])

    def test_color_no_data(self):
        self.send_signal("Data", None)
        self.widget.controls.value_type.buttons[1].click()
        self.widget.imageplot.update_color_schema()

    def test_save_graph(self):
        self.send_signal("Data", self.iris)
        with set_png_graph_save() as fname:
            self.widget.save_graph()
            self.assertGreater(os.path.getsize(fname), 1000)

    def test_unknown_values_axes(self):
        data = Orange.data.Table("iris")
        data.Y[0] = np.nan
        self.send_signal("Data", data)
        self.assertTrue(self.widget.Information.not_shown.is_shown())
