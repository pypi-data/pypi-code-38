from ftw.builder import builder_registry
from ftw.builder.dexterity import DexterityBuilder
from ftw.simplelayout.tests import builders
from ftw.slider.tests import builders


class SliderBlockBuilder(DexterityBuilder):
    portal_type = 'ftw.sliderblock.SliderBlock'

builder_registry.register('sliderblock', SliderBlockBuilder)
