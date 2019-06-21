import os
from qgis.core import QgsVectorLayer, QgsApplication
from PyQt5.QtGui import QColor


TEST_LAYER_NAMES = ['station', 'street', 'building']


def get_data_path():
    return os.path.join(os.path.dirname(__file__), 'testdata')


def create_layers(format='gml'):
    data_path = get_data_path()
    return [QgsVectorLayer(
        os.path.join(data_path, '{}.{}'.format(l, format)), l, 'ogr')
        for l in TEST_LAYER_NAMES]


def set_single_symbol(layers):
    lst = []
    for layer in layers:
        layer.renderer().symbol().setColor(QColor.fromRgb(0, 225, 0))
        lst.append(layer)
    return lst


def get_qgis_dir():
    return QgsApplication.prefixPath()
