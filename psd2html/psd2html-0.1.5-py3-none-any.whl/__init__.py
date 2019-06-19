from psd2html.builder.core import HtmlBuilder
from psd2html.converter.core import LayerConverter
from psd2html.io import PSDReader, HTMLWriter
from psd_tools import PSDImage


def psd2html(input, output=None):
    converter = PSD2HTML(resource_path='files/')
    return converter.convert(input, output)


class PSD2HTML(LayerConverter, PSDReader, HTMLWriter, HtmlBuilder):

    def __init__(self, resource_path=None):
        self.resource_path = resource_path

    def reset(self):
        """Reset the converter."""
        self._psd = None

    def convert(self, layer, output=None):
        self.reset()
        self._set_input(layer)
        self._set_output(output)

        layer = self._layer

        # Initialize html template
        self._html = HtmlBuilder()

        # Layerless PSDImage.
        if isinstance(layer, PSDImage) and len(layer) == 0 and layer.has_preview():
            self._html.add(
                self._html.image(self._get_image_href(layer.topil()), width=layer.width, height=layer.height)
            )
        else:
            # convert PSD layers to HTML elements
            elements = self.convert_layer(layer)
            self._html.add(elements)

            # save HTML to file
        html_content = self._html.get()
        return self._save_html(html_content)
