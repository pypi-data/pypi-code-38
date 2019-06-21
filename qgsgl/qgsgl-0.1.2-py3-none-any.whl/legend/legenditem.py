import os
from PyQt5.QtCore import QSize


class LegendItem:
    def __init__(self, qgis_symbol=None, item_name=None, **kwargs):
        self._qgis_symbol = qgis_symbol
        self._item_name = item_name
        self._size = kwargs.get('size', QSize(30, 30))
        self.label = kwargs.get('label', '')
        self.layers = kwargs.get('layers', [])

    @property
    def name(self):
        '''
        Return the name of the item
        '''
        return self._item_name

    def set_size(self, size):
        '''
        Set the output size of the image
        '''
        if isinstance(size, QSize):
            self._size = size
        else:
            raise TypeError('size must be a QSize object')

    def get_filename(self, format):
        return f'{self._item_name}.{format.lower()}'

    def has_image(self):
        return bool(self._qgis_symbol and self._item_name)

    def render(self, path, format='SVG'):
        '''
        Export the image to file system
        '''
        if self.has_image():
            self._qgis_symbol.exportImage(
                os.path.join(path, self.get_filename(format)),
                format,
                self._size
            )
