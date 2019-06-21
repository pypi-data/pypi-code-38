from .base import BaseLayer
from ..utils import get_rgba
from qgis.core import QgsSimpleFillSymbolLayer
from PyQt5.QtCore import Qt


class FillLayer(BaseLayer):

    SUPPORTED_SYMBOL_LAYER = (QgsSimpleFillSymbolLayer)

    def __init__(self, qgis_symbol_layer, **kwargs):
        self.opacity = kwargs.get('opacity', 1)
        super().__init__(qgis_symbol_layer)

    @classmethod
    def supports_symbol_layer(cls, symbol_layer):
        return isinstance(symbol_layer, cls.SUPPORTED_SYMBOL_LAYER)

    def _get_fill_color(self):
        if self.qgis_symbol_layer.brushStyle() == Qt.NoBrush:
            return 'rgba(0, 0, 0, 0)'
        else:
            return get_rgba(self.qgis_symbol_layer.color())

    def get_paint_properties(self):
        return {
            'fill-color': self._get_fill_color(),
            'fill-opacity': self.opacity
        }

    def get_layout_properties(self):
        pass

    def get_type(self):
        return 'fill'
