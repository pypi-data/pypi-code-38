from ftw.builder.dexterity import DexterityBuilder
from ftw.builder import builder_registry
from ftw.simplelayout.tests import builders


class SubsiteBuilder(DexterityBuilder):

    portal_type = 'ftw.subsite.Subsite'

    def with_language(self, language_code):
        if 'title' not in self.arguments:
            return self.having(force_language=language_code,
                               title=language_code)
        else:
            return self.having(force_language=language_code)


builder_registry.register('subsite', SubsiteBuilder)
