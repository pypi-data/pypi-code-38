from .base import BaseExpression
from ..symbol import Symbol
from qgis.core import QgsSingleSymbolRenderer, QgsCategorizedSymbolRenderer, \
    QgsGraduatedSymbolRenderer


class Expression(BaseExpression):
    def __init__(self, renderer, prop):
        super().__init__(renderer, prop)

    def get_json(self):
        if isinstance(self.renderer, QgsSingleSymbolRenderer):
            symbol = Symbol(self.renderer.symbol(), self.prop)
            return symbol.get_json()
        if isinstance(self.renderer, QgsCategorizedSymbolRenderer):
            json = ['match', ['get', self.renderer.classAttribute()]]
            for category in self.renderer.categories():
                symbol = Symbol(category.symbol(), self.prop)
                json.extend([category.value, symbol.get_json()])
            return json
        if isinstance(self.renderer, QgsGraduatedSymbolRenderer):
            raise NotImplementedError
