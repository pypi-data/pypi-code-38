from qgis.core import QgsSingleSymbolRenderer, QgsCategorizedSymbolRenderer, \
    QgsGraduatedSymbolRenderer

from ..glyphs import default_library
from ..layer import CircleLayer, FillLayer, LabelLayer, LineLayer, \
    SymbolLayer
from ..legend import LegendItem
from ..sprite import SpriteImage


class LayerConverter:
    def __init__(self, qgis_layer, source_id, source_layer_id=None, **kwargs):
        self._qgis_layer = qgis_layer
        self._renderer = qgis_layer.renderer()
        self._source_id = source_id
        self._source_layer_id = source_layer_id

        self._next_id = 0
        self._legend_id = 0

        self._base_id = kwargs.get('base_id', self._qgis_layer.id())
        self._visible = kwargs.get('visible', True)
        self._min_zoom = kwargs.get('min_zoom', 0)
        self._max_zoom = kwargs.get('max_zoom', 24)

        self._font_library = kwargs.get('font_library', default_library)
        self._legend = kwargs.get('legend', False)
        self._legend_item_size = kwargs.get('legend_item_size', None)

        self._circle_class = kwargs.get('circle_class', CircleLayer)
        self._fill_class = kwargs.get('fill_class', FillLayer)
        self._label_class = kwargs.get('label_class', LabelLayer)
        self._line_class = kwargs.get('line_class', LineLayer)
        self._symbol_class = kwargs.get('symbol_class', SymbolLayer)

        self.layers = []
        self.images = []
        self.legend_items = []

    def _get_id(self):
        self._next_id += 1
        return '{}_{}'.format(self._base_id, self._next_id)

    def _get_legend_id(self):
        self._legend_id += 1
        return '{}_{}'.format(self._base_id, self._legend_id)

    def _add_layer_legend_item(self):
        self.legend_items.insert(0, LegendItem(
            label=self._qgis_layer.name(),
            layers=[l['id'] for l in self.layers]))

    def _get_layer_json(self, gl_layer, id, **options):
        layer = {
            'id': id,
            'type': gl_layer.get_type(),
            'source': self._source_id,
        }

        if self._source_layer_id:
            layer['source-layer'] = self._source_layer_id

        filter = options.get('filter', None)
        if filter:
            layer['filter'] = filter

        if self._min_zoom > 0:
            layer['minzoom'] = self._min_zoom

        if self._max_zoom < 24:
            layer['maxzoom'] = self._max_zoom

        layer['layout'] = gl_layer.get_layout_properties() or {}

        paint = gl_layer.get_paint_properties()
        if paint:
            layer['paint'] = paint

        if (not self._visible) or options.get('visible', None) is False:
            layer['layout']['visibility'] = 'none'

        return layer

    def _get_layer_classes(self, symbol_layer):
        layer_classes = [
            self._circle_class,
            self._line_class,
            self._fill_class,
            self._symbol_class]

        return [cls for cls in layer_classes
                if cls.supports_symbol_layer(symbol_layer)]

    def _convert_symbol(self, symbol, **options):
        layers = []
        if self._qgis_layer.labelsEnabled():
            gl_layer = self._label_class(
                symbol,
                self._qgis_layer.labeling(),
                font_library=self._font_library)
            id = self._get_id()
            layer_json = self._get_layer_json(
                gl_layer, id, opacity=self._qgis_layer.opacity())
            layers.append(layer_json)

        for symbol_layer in symbol.symbolLayers():
            for layer_class in self._get_layer_classes(symbol_layer):
                id = self._get_id()
                gl_layer = layer_class(
                    symbol_layer, id=id, opacity=symbol.opacity())
                layer_json = self._get_layer_json(gl_layer, id, **options)
                layers.append(layer_json)
                if layer_class == self._symbol_class:
                    # symbol_layer needs to be cloned to keep it in memory.
                    self.images.append(SpriteImage(symbol_layer.clone(), id))

        layers.reverse()
        self.layers.extend(layers)

        if self._legend:
            # The symbol needs to be cloned to keep it in memory.
            # Otherwise, the Python interpreter garbage collects it
            # prematurely, causing segmentation faults.
            legend_options = {}
            if self._legend_item_size:
                legend_options['size'] = self._legend_item_size
            # We only include GL layers for single symbol renderers since
            # the layers for categorized and graduated renderers are included
            # in the parent legend item. This behavior may change once
            # gl-legend and gl-legend-item are restructured.
            if options.get('single', False):
                legend_options['layers'] = [l['id'] for l in layers]
            self.legend_items.append(LegendItem(
                symbol.clone(), self._get_legend_id(),
                label=options.get('name', ''),
                **legend_options))

    def _convert_single(self):
        self._convert_symbol(
            self._renderer.symbol(),
            name=self._qgis_layer.name(),
            single=True)

    def _convert_categorized(self):
        values = []
        getter = ['get', self._renderer.classAttribute()]

        for category in self._renderer.categories():
            visible = category.renderState()
            value = category.value()

            if value is not '':
                values.append(value)
                filter = ['==', getter, value]
            else:
                filter = ['all']
                for value in values:
                    filter.append(['!=', getter, value])

            self._convert_symbol(
                category.symbol(),
                filter=filter,
                visible=visible,
                name=category.label())

        if self._legend:
            self._add_layer_legend_item()

    def _convert_graduated(self):
        ends = set()
        getter = ['get', self._renderer.classAttribute()]

        for range in self._renderer.ranges():
            visible = range.renderState()
            lower = range.lowerValue()
            upper = range.upperValue()
            filter = ['all']

            if lower is not None:
                op = '>' if lower in ends else '>='
                ends.add(lower)
                filter.append([op, getter, lower])

            if upper is not None:
                op = '<' if upper in ends else '<='
                ends.add(upper)
                filter.append([op, getter, upper])

            self._convert_symbol(
                range.symbol(),
                filter=filter,
                visible=visible,
                name=range.label())

        if self._legend:
            self._add_layer_legend_item()

    def convert(self):
        self.layers = []
        self.images = []
        self.legend_items = []

        if isinstance(self._renderer, QgsSingleSymbolRenderer):
            return self._convert_single()
        if isinstance(self._renderer, QgsCategorizedSymbolRenderer):
            return self._convert_categorized()
        if isinstance(self._renderer, QgsGraduatedSymbolRenderer):
            return self._convert_graduated()
