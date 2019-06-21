from ..utils import map_unit_to_pixel
from qgis.core import QgsMarkerSymbol, QgsLineSymbol, QgsFillSymbol


class LabelLayer():
    def __init__(self, qgis_symbol, labeling, **kwargs):
        self._qgis_symbol = qgis_symbol
        self._labeling = labeling
        self._settings = self._labeling.settings()
        self._format = self._settings.format()
        self._text_buffer = self._format.buffer()
        self._font = self._format.font()
        self._expression = self._settings.getLabelExpression()
        self._font_library = kwargs.get('font_library')

    def _get_symbol_placement(self):
        if isinstance(self._qgis_symbol, QgsMarkerSymbol) or \
           isinstance(self._qgis_symbol, QgsFillSymbol):
            return 'point'
        elif isinstance(self._qgis_symbol, QgsLineSymbol):
            return 'line'
        else:
            return 'point'

    def _get_text_size(self):
        return map_unit_to_pixel(
            self._format.size(), self._format.sizeUnit()
        )

    def _get_text_offset(self):
        offset = [0, 0]
        if isinstance(self._qgis_symbol, QgsMarkerSymbol):
            symbol_size = map_unit_to_pixel(
                self._qgis_symbol.size(),
                self._qgis_symbol.sizeUnit()
            )
            text_size = self._get_text_size()
            offset = [(symbol_size / text_size) / 2,
                      -(symbol_size / text_size) / 2]
            return offset
        return offset

    def get_layout_properties(self):
        layout = {
            'symbol-placement': self._get_symbol_placement(),
            'text-field': [
                'get', self._expression.dump()
            ],
            'text-size': self._get_text_size(),
            'text-font': [
                self._font_library.get_font_name(
                    self._font.family(),
                    self._font.weight(),
                    self._font.italic())
            ],
            'text-letter-spacing': self._font.letterSpacing(),
            'text-offset': self._get_text_offset(),
            'text-anchor': 'bottom-left'
        }
        return layout

    def get_paint_properties(self):
        layout = {
            'text-color': self._format.color().name(),
        }

        if self._text_buffer.enabled():
            qcolor = self._format.buffer().color()
            color = (
                qcolor.red(),
                qcolor.green(),
                qcolor.blue(),
                self._format.buffer().opacity()
            )
            buffer_width = map_unit_to_pixel(
                self._format.buffer().size(),
                self._format.buffer().sizeUnit()
            )
            layout['text-halo-color'] = f'rgba{color}'
            layout['text-halo-width'] = buffer_width
        return layout

    def get_type(self):
        return 'symbol'
