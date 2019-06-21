from .base import BaseSource
from .exceptions import LayerNotSetError


class GeoJSONSource(BaseSource):

    def __init__(self, id, url=None, **kwargs):
        super().__init__(id, url)
        self.layer = None
        self.layer_id = None
        self.attributes = []

    def add_layer(self, layer, id=None, **kwargs):
        """Add data from a layer to the source."""

        self.layer = layer
        self.layer_id = id or layer.id()
        self.attributes = kwargs.get('attributes', [])

    def get_layer_id(self, layer):
        """Given a QGIS layer, get the source's layer ID."""

        return None

    def get_json(self):
        """Create a dictionary representing the source for use in the style."""

        return {
            'type': 'geojson',
            'url': self.url
        }

    def write(self, path):
        """Write the layer data to the given path."""

        if self.layer is None:
            raise LayerNotSetError('Source does not have an associated layer')

        self._write_layer(
            self.layer, path, 'GeoJSON', self.layer_id, False, 4326,
            attributes=self.attributes)
