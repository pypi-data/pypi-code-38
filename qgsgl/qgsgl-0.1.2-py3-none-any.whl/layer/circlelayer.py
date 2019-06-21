from .base import BaseLayer
from ..utils import map_unit_to_pixel, convert_outline_width, get_rgba
from qgis.core import QgsSimpleMarkerSymbolLayerBase, \
    QgsSimpleMarkerSymbolLayer


class CircleLayer(BaseLayer):

    SUPPORTED_SYMBOL_LAYER = (QgsSimpleMarkerSymbolLayer)

    def __init__(self, qgis_symbol_layer, **kwargs):
        self.opacity = kwargs.get('opacity', 1)
        super().__init__(qgis_symbol_layer)

    @classmethod
    def supports_symbol_layer(cls, symbol_layer):
        if isinstance(symbol_layer, cls.SUPPORTED_SYMBOL_LAYER):
            if symbol_layer.shape() == \
                    QgsSimpleMarkerSymbolLayerBase.Circle:
                return True
        return False

    def get_paint_properties(self, output_dpi=None):
        return {
            'circle-color': get_rgba(self.qgis_symbol_layer.color()),
            'circle-radius': map_unit_to_pixel(
                self.qgis_symbol_layer.size() / 2,
                self.qgis_symbol_layer.sizeUnit(),
                output_dpi
            ),
            'circle-stroke-color': get_rgba(
                self.qgis_symbol_layer.strokeColor()),
            'circle-stroke-width': convert_outline_width(
                self.qgis_symbol_layer),
            'circle-opacity': self.opacity
        }

    def get_layout_properties(self):
        pass

    def get_type(self):
        return 'circle'
