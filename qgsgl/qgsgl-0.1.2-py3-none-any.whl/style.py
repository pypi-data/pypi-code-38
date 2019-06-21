from .converters import LayerConverter
from .glyphs import default_library
from .legend import Legend
from .sprite import Sprite


class Style:
    def __init__(self, **kwargs):
        self.sources = {}
        self.layers = []
        self.legend = Legend()
        self.sprite = Sprite()

        self.font_library = kwargs.get('font_library', default_library)
        self.glyphs_url = kwargs.get('glyphs_url', '')
        self.sprite_url = kwargs.get('sprite_url', '')
        self.layer_converter_class = kwargs.get(
            'layer_converter_class', LayerConverter)

    def add_source(self, source):
        self.sources[source.id] = source.get_json()

    def add_layer(self, qgis_layer, source_id, source_layer_id=None, **kwargs):
        converter = self.layer_converter_class(
            qgis_layer, source_id, source_layer_id,
            font_library=self.font_library,
            **kwargs)

        converter.convert()
        self.layers.extend(converter.layers)

        for image in converter.images:
            self.sprite.add_image(image)

        for item in converter.legend_items:
            self.legend.add_item(item)

        return [l['id'] for l in converter.layers]

    def get_json(self):
        style = {
            "version": 8,
            "sources": self.sources,
            "layers": list(reversed(self.layers)),
        }

        if self.sprite_url and self.sprite.has_images():
            style['sprite'] = self.sprite_url

        if self.glyphs_url:
            style['glyphs'] = self.glyphs_url

        return style

    def write_legend(self, path, format='SVG'):
        self.legend.render(path, format)

    def write_sprite(self, path, scale):
        if not self.sprite.has_images():
            return

        self.sprite.render(path, scale)
