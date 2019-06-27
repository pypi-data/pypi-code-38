from contextlib import contextmanager
from unittest.mock import patch

from AnyQt.QtTest import QTest
from AnyQt.QtCore import Qt

import Orange
from Orange.tests import named_file
from Orange.widgets.io import PngFormat


@contextmanager
def hold_modifiers(widget, modifiers):
    # use some unexisting key
    QTest.keyPress(widget, Qt.Key_F35, modifiers)
    try:
        yield
    finally:
        QTest.keyRelease(widget, Qt.Key_F35)


def smaller_data(data, nth_instance, nth_feature):
    natts = [a for i, a in enumerate(data.domain.attributes)
             if i % nth_feature == 0]
    data = data[::nth_instance]
    ndomain = Orange.data.Domain(natts, data.domain.class_vars,
                                 metas=data.domain.metas)
    return data.transform(ndomain)


@contextmanager
def set_png_graph_save():
    with named_file("", suffix=".png") as fname:
        with patch("Orange.widgets.utils.filedialogs.open_filename_dialog_save",
                   lambda *x: (fname, PngFormat, None)):
            yield fname
