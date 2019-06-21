from .base import BaseLayer
from qgis.core import QgsLineSymbolLayer, QgsFillSymbolLayer, \
    QgsSimpleLineSymbolLayer, QgsSimpleFillSymbolLayer
from ..utils import convert_outline_width, get_rgba
from PyQt5.QtCore import Qt


def get_qt_pen_style(qgis_symbol_layer):
    if isinstance(qgis_symbol_layer, QgsLineSymbolLayer):
        return qgis_symbol_layer.penStyle()
    elif isinstance(qgis_symbol_layer, QgsFillSymbolLayer):
        return qgis_symbol_layer.strokeStyle()


class LineLayer(BaseLayer):

    SUPPORTED_SYMBOL_LAYER = (
        QgsSimpleLineSymbolLayer,
        QgsSimpleFillSymbolLayer)

    def __init__(self, qgis_symbol_layer, **kwargs):
        self.opacity = kwargs.get('opacity', 1)
        self._hairline_width = kwargs.get('hairline_width', 0.2)
        super().__init__(qgis_symbol_layer)

    @classmethod
    def supports_symbol_layer(cls, symbol_layer):
        if isinstance(symbol_layer, cls.SUPPORTED_SYMBOL_LAYER):
            return get_qt_pen_style(symbol_layer) not in [None, Qt.NoPen]
        return False

    def _get_pen_style(self):
        style = get_qt_pen_style(self.qgis_symbol_layer)
        if style == Qt.SolidLine:
            return None
        elif style == Qt.DashLine:
            return [5, 5]
        elif style == Qt.DotLine:
            return [1, 1]
        elif style == Qt.DashDotLine:
            return [5, 5, 1, 5]
        elif style == Qt.DashDotDotLine:
            return [5, 5, 1, 5, 1, 5]
        elif style == Qt.NoPen:
            return [0]
        else:
            return None

    def _get_line_cap(self):
        cap_style = self.qgis_symbol_layer.penCapStyle()
        if cap_style == Qt.SquareCap:
            return 'square'
        elif cap_style == Qt.FlatCap:
            return 'butt'
        elif cap_style == Qt.RoundCap:
            return 'round'
        else:
            return 'square'

    def _get_line_join(self):
        join_style = self.qgis_symbol_layer.penJoinStyle()
        if join_style == Qt.MiterJoin:
            return 'miter'
        elif join_style == Qt.BevelJoin:
            return 'bevel'
        elif join_style == Qt.RoundJoin:
            return 'round'
        else:
            return 'miter'

    def _get_line_width(self):
        return convert_outline_width(self.qgis_symbol_layer)

    def _get_line_paint_property(self, output_dpi):
        paint_prop = {
            'line-color': get_rgba(self.qgis_symbol_layer.color()),
            'line-width': convert_outline_width(self.qgis_symbol_layer,
                                                output_dpi),
            'line-opacity': self.opacity
        }
        pen_style = self._get_pen_style()
        if pen_style is not None:
            paint_prop['line-dasharray'] = pen_style
        return paint_prop

    def _get_border_paint_property(self, output_dpi):
        paint = {
            'line-color': get_rgba(self.qgis_symbol_layer.strokeColor()),
            'line-width': convert_outline_width(self.qgis_symbol_layer,
                                                output_dpi)
        }
        pen_style = self._get_pen_style()

        if pen_style is not None:
            paint['line-dasharray'] = pen_style
        return paint

    def _get_line_layout_property(self):
        return {
            'line-cap': self._get_line_cap(),
            'line-join': self._get_line_join()
        }

    def _get_border_layout_property(self):
        pass

    def get_paint_properties(self, output_dpi=None):
        if isinstance(self.qgis_symbol_layer, QgsLineSymbolLayer):
            return self._get_line_paint_property(output_dpi)
        elif isinstance(self.qgis_symbol_layer, QgsFillSymbolLayer):
            return self._get_border_paint_property(output_dpi)
        else:
            raise TypeError()

    def get_layout_properties(self):
        if isinstance(self.qgis_symbol_layer, QgsLineSymbolLayer):
            return self._get_line_layout_property()
        elif isinstance(self.qgis_symbol_layer, QgsFillSymbolLayer):
            return self._get_border_layout_property()

    def get_type(self):
        return 'line'
