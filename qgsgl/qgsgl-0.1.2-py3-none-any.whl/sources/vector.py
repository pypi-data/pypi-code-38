import json
import os
import platform
import subprocess
from tempfile import TemporaryDirectory
from qgis.core import QgsSettings
from .base import BaseSource
from .exceptions import OGRError


class VectorSource(BaseSource):

    def __init__(self, id, url=None, **kwargs):
        super().__init__(id, url)
        self.name = kwargs.get('name', None)
        self.description = kwargs.get('description', None)
        self.min_zoom = kwargs.get('min_zoom', None)
        self.max_zoom = kwargs.get('max_zoom', None)
        self.layer_id_map = {}
        self.layers = []

    def _get_env(self):
        pth = os.getenv('PATH')
        env = {}
        env['PATH'] = pth

        is_darwin = platform.system() == 'Darwin'
        if is_darwin:
            gdal_path = '/Library/Frameworks/GDAL.framework/Programs'
        else:
            settings = QgsSettings()
            gdal_path = settings.value('/GdalTools/gdalPath', '')

        if not gdal_path.lower() in pth.lower().split(os.pathsep):
            env['PATH'] = ''.join([pth, os.pathsep, gdal_path])

        return env

    def add_layer(self, layer, **kwargs):
        """Add data from a layer to the source."""

        kwargs['id'] = kwargs.get('id', layer.id())
        kwargs['max_zoom'] = kwargs.get('max_zoom', 22)
        kwargs['min_zoom'] = kwargs.get('min_zoom', 0)

        if kwargs['max_zoom'] > 22:
            raise ValueError('max_zoom must be 22 or less')

        if kwargs['min_zoom'] < 0:
            raise ValueError('min_zoom must be 0 or greater')

        self.layer_id_map[layer.id()] = kwargs['id']
        self.layers.append((layer, kwargs))

    def get_layer_id(self, layer):
        """Given a QGIS layer, get the source's layer ID."""

        return self.layer_id_map[layer.id()]

    def get_json(self):
        """Create a dictionary representing the source for use in the style."""

        return {
            'type': 'vector',
            'url': self.url
        }

    def write(self, path):
        """Write the layer data to the given path."""

        layer_conf = {}

        with TemporaryDirectory() as temp_dir:
            gpkg_path = os.path.join(temp_dir, 'data.gpkg')
            min_zoom = 22
            max_zoom = 0
            for i, (layer, options) in enumerate(self.layers):
                self._write_layer(
                    layer, gpkg_path, 'GPKG', options['id'], i > 0,
                    attributes=options.get('attributes', []))
                layer_conf[options['id']] = {
                    'minzoom': options['min_zoom'],
                    'maxzoom': options['max_zoom'],
                    'description': options.get('description', '')
                }
                if options['max_zoom'] > max_zoom:
                    max_zoom = options['max_zoom']
                if options['min_zoom'] < min_zoom:
                    min_zoom = options['min_zoom']

            if self.min_zoom is None:
                self.min_zoom = min_zoom
            if self.max_zoom is None:
                self.max_zoom = max_zoom

            cmd = ['ogr2ogr', '-f', 'MBTILES', path, gpkg_path]

            if self.name:
                cmd.extend(['-dsco', 'NAME={}'.format(self.name)])

            if self.description:
                cmd.extend(
                    ['-dsco', 'DESCRIPTION={}'.format(self.description)])

            if self.min_zoom is not None:
                cmd.extend(['-dsco', 'MINZOOM={}'.format(self.min_zoom)])

            if self.max_zoom is not None:
                cmd.extend(['-dsco', 'MAXZOOM={}'.format(self.max_zoom)])

            cmd.extend(['-dsco', 'CONF={}'.format(json.dumps(layer_conf))])

            # All Popen handles need to be mapped, or Windows 7 gets an error.
            # See: https://bugs.python.org/issue3905
            ogr_kwargs = {
                'stdin': subprocess.PIPE,
                'stderr': subprocess.STDOUT,
                'env': self._get_env(),
            }

            if platform.system() == 'Windows':
                # Hide the ogr2ogr window on Windows
                si = subprocess.STARTUPINFO()
                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                ogr_kwargs['startupinfo'] = si

            try:
                subprocess.check_output(cmd, **ogr_kwargs)
            except subprocess.CalledProcessError as err:
                raise OGRError(err.output)
