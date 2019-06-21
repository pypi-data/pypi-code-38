# Utils function for qgsgl
from qgis.core import QgsMapSettings, QgsRenderContext, \
    QgsMarkerSymbolLayer, QgsLineSymbolLayer, QgsFillSymbolLayer
from PyQt5.QtCore import Qt


def map_unit_to_pixel(value, value_unit, output_dpi=None):
    ms = QgsMapSettings()
    if output_dpi:
        ms.setOutputDpi(output_dpi)
    rc = QgsRenderContext.fromMapSettings(ms)
    return rc.convertToPainterUnits(value, value_unit) / ms.devicePixelRatio()


def convert_outline_width(qgis_symbol_layer, output_dpi=None):
    if isinstance(qgis_symbol_layer, QgsMarkerSymbolLayer):
        pen_style = 'strokeStyle'
        width = 'strokeWidth'
        width_unit = f'{width}Unit'
    elif isinstance(qgis_symbol_layer, QgsLineSymbolLayer):
        pen_style = 'penStyle'
        width = 'width'
        width_unit = f'{width}Unit'
    elif isinstance(qgis_symbol_layer, QgsFillSymbolLayer):
        pen_style = 'dxfPenStyle'
        width = 'strokeWidth'
        width_unit = f'{width}Unit'

    if getattr(qgis_symbol_layer, width)() == 0 and \
       getattr(qgis_symbol_layer, pen_style)() != Qt.NoPen:
        return 1
    elif getattr(qgis_symbol_layer, pen_style)() == Qt.NoPen:
        return 0
    else:
        return map_unit_to_pixel(
            getattr(qgis_symbol_layer, width)(),
            getattr(qgis_symbol_layer, width_unit)(),
            output_dpi
        )


def get_rgba(qcolor):
    color = (
        qcolor.red(),
        qcolor.green(),
        qcolor.blue(),
        qcolor.alpha() / 255
    )
    return f'rgba{color}'
