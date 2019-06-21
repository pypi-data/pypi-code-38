

class BaseSymbol:
    def __init__(self, qgis_symbol, prop):
        self.qgis_symbol = qgis_symbol
        self.prop = prop

    def get_json(self):
        """ Implement by a child class"""

        raise NotImplementedError
