from ftw.builder import builder_registry
from ftw.builder.dexterity import DexterityBuilder
from plone.namedfile.file import NamedImage
from StringIO import StringIO


class SliderContainerBuilder(DexterityBuilder):
    portal_type = 'ftw.slider.Container'

builder_registry.register('slider container', SliderContainerBuilder)


class SliderPaneBuilder(DexterityBuilder):
    portal_type = 'ftw.slider.Pane'

    def with_dummy_image(self):
        dummy_image = StringIO(
            'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\x00\x00'
            '\x00!\xf9\x04\x04\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00'
            '\x01\x00\x00\x02\x02D\x01\x00;')

        self.arguments["image"] = NamedImage(dummy_image.read(),
                                                 filename=u"image.gif")
        return self

builder_registry.register('slider pane', SliderPaneBuilder)
