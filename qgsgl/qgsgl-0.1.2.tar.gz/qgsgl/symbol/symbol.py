from .base import BaseSymbol


class Symbol(BaseSymbol):
    def __init__(self, qgis_symbol, prop):
        super().__init__(qgis_symbol, prop)
        self.color = ['circle-color', 'line-color', 'fill-color']
        self.opacity = ['circle-opacity', 'line-opacity', 'fill-opacity']

    def get_type(self):
        type = self.qgis_symbol.type()
        if type == 0:
            return 'circle'
        elif type == 1:
            return 'line'
        elif type == 2:
            return 'fill'
        else:
            return 'unknown'

    def get_json(self):
        properties = self.qgis_symbol.symbolLayers()[0].properties()

        if self.prop in self.color:
            return self.qgis_symbol.color().name()
        if self.prop == 'circle-radius':
            return self.qgis_symbol.size()
        if self.prop in self.opacity:
            return self.qgis_symbol.opacity()
        if self.prop == 'circle-stroke-width':
            return float(properties['outline_width'])
        if self.prop == 'circle-stroke-color':
            return properties['outline_color']
        if self.prop == 'line-width':
            return self.qgis_symbol.width()
        if self.prop == 'fill-outline-color':
            return properties['outline_color']
        if self.prop == 'fill-outline-width':
            return float(properties['outline_width'])
        if self.prop == 'fill-outline-style':
            return properties['outline_style']
