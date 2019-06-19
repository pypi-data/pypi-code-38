from ftw.builder import builder_registry
from ftw.builder.dexterity import DexterityBuilder


class DXContainerBuilder(DexterityBuilder):
    portal_type = 'DXContainer'


builder_registry.register('dx container', DXContainerBuilder)
