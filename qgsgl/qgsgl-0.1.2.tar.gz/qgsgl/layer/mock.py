class MockLayer:
    def __init__(self, qgis_layer=None):
        pass

    def get_type(self):
        return 'mock'

    def get_layout_properties(self):
        return {}

    def get_paint_properties(self):
        return {}
