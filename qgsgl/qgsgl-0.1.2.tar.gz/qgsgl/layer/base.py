

class BaseLayer:
    def __init__(self, qgis_symbol_layer, **kwargs):
        self.qgis_symbol_layer = qgis_symbol_layer
        self.properties = self.qgis_symbol_layer.properties()

    @classmethod
    def supports_symbol_layer(cls, symbol_layer):
        """Check to see if the symbol_layer is supported"""

        raise NotImplementedError()

    def get_paint_properties(self):
        """Get paint property from qgis symbol"""

        raise NotImplementedError()

    def get_layout_properties(self):
        """Get paint property from qgis symbol"""

        raise NotImplementedError()

    def get_type(self):
        """Get type based on the qgis type"""

        raise NotImplementedError()
