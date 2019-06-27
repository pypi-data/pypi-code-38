from unittest.mock import patch, MagicMock

import numpy as np

from AnyQt.QtCore import QPointF
from AnyQt.QtWidgets import QToolTip

import Orange
from Orange.widgets.tests.base import WidgetTest

from orangecontrib.spectroscopy.widgets.owspectralseries import OWSpectralSeries
from orangecontrib.spectroscopy.preprocess import Interpolate

NAN = float("nan")


class TestOWSpectralSeries(WidgetTest):

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
        self.widget = self.create_widget(OWSpectralSeries)

    def try_big_selection(self):
        all_select = None if self.widget.data is None else [1]*len(self.widget.data)
        self.widget.imageplot.make_selection(all_select, True)
        self.widget.imageplot.make_selection(None, True)

    def test_strange(self):
        for data in self.strange_data:
            self.send_signal("Data", data)
            self.try_big_selection()

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

    def test_select_click(self):
        self.send_signal("Data", self.whitelight)
        self.widget.imageplot.select_by_click(QPointF(1, 2), False)
        # work by indices
        out = self.get_output("Selection")
        np.testing.assert_equal(out.metas[:, 0], 1)
        np.testing.assert_equal(out.metas[:, 1], 0)
        # select a feature
        self.widget.imageplot.attr_x = "x"
        self.widget.imageplot.update_attr()
        self.widget.imageplot.select_by_click(QPointF(1, 2), False)
        out = self.get_output("Selection")
        np.testing.assert_equal(out.metas[:, 0], 1)
        np.testing.assert_equal(out.metas[:, 1], np.arange(100))

    def test_single_update_view(self):
        uw = "orangecontrib.spectroscopy.widgets.owspectralseries.LineScanPlot.update_view"
        with patch(uw) as p:
            self.send_signal("Data", self.iris)
            self.assertEqual(p.call_count, 1)

    def test_tooltip(self):
        data = self.iris
        self.send_signal(self.widget.Inputs.data, data)

        event = MagicMock()
        with patch.object(self.widget.imageplot.plot.vb, "mapSceneToView"), \
                patch.object(QToolTip, "showText") as show_text:

            sel = np.zeros(len(data), dtype="bool")

            sel[3] = 1  # a single instance
            with patch.object(self.widget.imageplot, "_points_at_pos",
                              return_value=(sel, 2)):
                self.assertTrue(self.widget.imageplot.help_event(event))
                (_, text), _ = show_text.call_args
                self.assertIn("iris = {}".format(data[3, "iris"]), text)
                self.assertIn("value = {}".format(data[3, 2]), text)
                self.assertEqual(1, text.count("iris ="))

            sel[51] = 1  # add a data point
            with patch.object(self.widget.imageplot, "_points_at_pos",
                              return_value=(sel, 2)):
                self.assertTrue(self.widget.imageplot.help_event(event))
                (_, text), _ = show_text.call_args
                self.assertIn("iris = {}".format(data[3, "iris"]), text)
                self.assertIn("iris = {}".format(data[51, "iris"]), text)
                self.assertIn("value = {}".format(data[3, 2]), text)
                self.assertIn("value = {}".format(data[51, 2]), text)
                self.assertEqual(2, text.count("iris ="))
