from .base import BaseLayer
from qgis.core import QgsMarkerSymbolLayer, QgsLineSymbolLayer, \
    QgsSvgMarkerSymbolLayer, QgsSimpleMarkerSymbolLayer, \
    QgsEllipseSymbolLayer, QgsFilledMarkerSymbolLayer, \
    QgsFontMarkerSymbolLayer, QgsSimpleMarkerSymbolLayerBase


class SymbolLayer(BaseLayer):

    SUPPORTED_SYMBOL_LAYER = (
        QgsSvgMarkerSymbolLayer,
        QgsSimpleMarkerSymbolLayer,
        QgsEllipseSymbolLayer,
        QgsFilledMarkerSymbolLayer,
        QgsFontMarkerSymbolLayer
    )

    def __init__(self, qgis_symbol_layer, **kwargs):
        super().__init__(qgis_symbol_layer)
        self.image_id = kwargs.get('image_id', kwargs.get('id', 'image'))
        self.opacity = kwargs.get('opacity', 1)

    @classmethod
    def supports_symbol_layer(cls, symbol_layer):
        if isinstance(symbol_layer, QgsSimpleMarkerSymbolLayer):
            if symbol_layer.shape() == QgsSimpleMarkerSymbolLayerBase.Circle:
                return False
        return isinstance(symbol_layer, cls.SUPPORTED_SYMBOL_LAYER)

    def _get_icon_layout(self):
        return {
            # return name of image
            'icon-image': self.image_id,
        }

    def _get_endpoint_layout(self):
        raise NotImplementedError()

    def get_paint_properties(self):
        return {
            'icon-opacity': self.opacity
        }

    def get_layout_properties(self):
        if isinstance(self.qgis_symbol_layer, QgsMarkerSymbolLayer):
            return self._get_icon_layout()
        elif isinstance(self.qgis_symbol_layer, QgsLineSymbolLayer):
            return self._get_endpoint_layer()

    def get_type(self):
        return 'symbol'
