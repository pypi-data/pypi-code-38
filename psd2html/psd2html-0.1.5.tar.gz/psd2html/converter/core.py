from psd2html.builder.core import Group
from psd_tools.api.layers import TypeLayer


class LayerConverter(object):

    def convert_layer(self, layer):
        """
        Convert the given layer.

        The current implementation always converts a PSD layer to a single
        HTML element.

        :return: HTML element.
        """
        if layer.is_group():
            element = self.create_group(layer)
        elif isinstance(layer, TypeLayer):
            element = self.create_text(layer)
            return element
        elif layer.has_pixels():
            element = self.create_image(layer)
        else:
            return None

        return element

    def create_group(self, group, container=None):
        if not container:
            kwargs = self.get_common_attrs(group)
            kwargs['class_name'] = group.name.replace(' ', '_').lower()
            container = Group(**kwargs)

            for layer in group:
                element = self.convert_layer(layer)
                if not element:
                    continue
                container.add(element)

        return container.get()

    def create_image(self, layer):
        """Create an image element."""
        kwargs = self.get_common_attrs(layer)
        kwargs['opacity'] = layer.opacity / 255.0
        element = self._html.image(
            self._get_image_href(layer.topil()),
            class_name=layer.kind + ' ' + layer.name.replace(' ', '_').lower(),
            **kwargs
        )  # To disable attribute validation.
        return element

    def get_common_attrs(self, layer):
        attrs = {
            'left': layer.left,
            'right': layer.right,
            'top': layer.top,
            'bottom': layer.bottom,
            'width': layer.width,
            'height': layer.height,
            'visible': layer.visible,
        }

        return attrs

    def create_text(self, layer):
        """Create a text element."""
        style_data = layer.engine_dict['StyleRun']['RunArray'][0]['StyleSheet']['StyleSheetData']
        fill = style_data.get('FillColor')['Values']
        rgb = 'rgb(' + str(int(255 * fill[1])) + ',' + str(int(255 * fill[2])) + ',' + str(int(255 * fill[3])) + ')'
        kwargs = self.get_common_attrs(layer)
        kwargs['opacity'] = layer.opacity / 255.0
        kwargs['class_name'] = 'text ' + layer.name.replace(' ', '_').lower(),
        kwargs['font_size'] = int(style_data['FontSize']),
        kwargs['color'] = rgb

        element = self._html.div(
            layer.text,
            **kwargs
        )

        return element
