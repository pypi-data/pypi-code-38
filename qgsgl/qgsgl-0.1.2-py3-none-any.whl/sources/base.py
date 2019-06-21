from qgis.core import QgsVectorFileWriter, QgsCoordinateTransform, \
    QgsProject, QgsCoordinateReferenceSystem


class BaseSource:

    def __init__(self, id, url=None):
        self.id = id
        self.url = url

    def add_layer(self, layer, **kwargs):
        """Add data from a layer to the source."""

        raise NotImplementedError

    def get_layer_id(self, layer):
        """Given a QGIS layer, get the source's layer ID."""

        raise NotImplementedError

    def get_json(self):
        """Create a dictionary representing the source for use in the style."""

        raise NotImplementedError

    def write(self, path):
        """Write the layer data to the given path."""

        raise NotImplementedError

    def _write_layer(self, layer, path, driver, layer_id,
                     update=False, srid=None, attributes=[]):
        """Write data for the given layer using the provided options."""

        options = QgsVectorFileWriter.SaveVectorOptions()
        options.actionOnExistingFile = \
            QgsVectorFileWriter.CreateOrOverwriteLayer if update \
            else QgsVectorFileWriter.CreateOrOverwriteFile
        options.driverName = driver
        options.layerName = layer_id
        if srid:
            options.ct = QgsCoordinateTransform(
                layer.sourceCrs(),
                QgsCoordinateReferenceSystem('EPSG:{}'.format(srid)),
                QgsProject.instance())
        if attributes:
            options.attributes = attributes
        QgsVectorFileWriter.writeAsVectorFormat(layer, path, options)
