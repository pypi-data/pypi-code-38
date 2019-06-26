from ftw.builder import Builder
from ftw.builder import create
from ftw.subsite.interfaces import ILanguages
from ftw.subsite.tests.base import IntegrationTestCase
from z3c.relationfield import RelationValue
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


def introduce_language_subsites(*subsites):
    intids = getUtility(IIntIds)

    for subsite in subsites:
        ids = [intids.getId(obj) for obj in subsites]
        ids.remove(intids.getId(subsite))
        subsite.language_references = [RelationValue(id_) for id_ in ids]


class TestLanguagesAdapterOnSubsite(IntegrationTestCase):

    def test_current_language_is_translated(self):
        german = create(Builder('subsite')
                        .titled(u'Subsite')
                        .with_language('de'))

        langs = getMultiAdapter((german, self.request), ILanguages)
        self.assertEquals(
            {'url': german.absolute_url(),
             'title': u'Deutsch',
             'code': 'de'},
            langs.get_current_language())

    def test_related_languages(self):
        german = create(Builder('subsite')
                        .titled(u'Subsite')
                        .with_language('de'))
        french = create(Builder('subsite')
                        .titled(u'Subsite')
                        .with_language('fr'))
        italian = create(Builder('subsite')
                         .titled(u'Subsite')
                         .with_language('it'))
        introduce_language_subsites(german, french, italian)

        langs = getMultiAdapter((german, self.request), ILanguages)
        self.assertEquals(
            [{'url': french.absolute_url(),
              'title': u'Fran\xe7ais',
              'code': 'fr'},

             {'url': italian.absolute_url(),
              'title': u'Italiano',
              'code': 'it'}],

            langs.get_related_languages())

    def test_related_languages_with_showing_site_root(self):
        german = create(Builder('subsite')
                        .titled(u'Subsite')
                        .with_language('de')
                        .having(link_site_in_languagechooser=True))
        french = create(Builder('subsite')
                        .titled(u'Subsite')
                        .with_language('fr')
                        .having(link_site_in_languagechooser=True))
        introduce_language_subsites(german, french)

        langs = getMultiAdapter((german, self.request), ILanguages)
        self.assertEquals(
            [{'url': self.portal.absolute_url(),
              'title': u'English',
              'code': 'en'},

             {'url': french.absolute_url(),
              'title': u'Fran\xe7ais',
              'code': 'fr'}],

            langs.get_related_languages())


class TestLanguagesAdapterOnPloneSite(IntegrationTestCase):

    def test_current_language_is_english(self):
        # The default site root language is english in the tests.
        langs = getMultiAdapter((self.portal, self.request), ILanguages)
        self.assertEquals(
            {'url': self.portal.portal_url(),
             'title': u'English',
             'code': 'en'},
            langs.get_current_language())

    def test_related_languages_lists_only_subsites_which_show_link(self):
        german = create(Builder('subsite')
                        .titled(u'Subsite')
                        .with_language('de')
                        .having(link_site_in_languagechooser=True))
        french = create(Builder('subsite')
                        .titled(u'Subsite')
                        .with_language('fr')
                        .having(link_site_in_languagechooser=True))
        create(Builder('subsite').titled(u'Subsite').with_language('it'))

        langs = getMultiAdapter((self.portal, self.request), ILanguages)
        self.assertEquals(
            [{'url': german.absolute_url(),
              'title': u'Deutsch',
              'code': 'de'},

             {'url': french.absolute_url(),
              'title': u'Fran\xe7ais',
              'code': 'fr'}],

            langs.get_related_languages())


class TestLanguagesAdapterOnSubsiteSubContent(IntegrationTestCase):

    def test_current_language_is_taken_from_next_parent_subsite(self):
        german = create(Builder('subsite')
                        .titled(u'Subsite')
                        .with_language('de'))
        folder = create(Builder('folder').within(german))

        langs = getMultiAdapter((folder, self.request), ILanguages)
        self.assertEquals(
            {'url': german.absolute_url(),
             'title': u'Deutsch',
             'code': 'de'},
            langs.get_current_language())

    def test_current_language_is_taken_from_parent_site_root(self):
        folder = create(Builder('folder'))

        langs = getMultiAdapter((folder, self.request), ILanguages)
        self.assertEquals(
            {'url': self.portal.portal_url(),
             'title': u'English',
             'code': 'en'},
            langs.get_current_language())

    def test_related_languages_is_inherited_from_parent_subsite(self):
        german = create(Builder('subsite')
                        .titled(u'Subsite')
                        .with_language('de')
                        .having(link_site_in_languagechooser=True))
        french = create(Builder('subsite')
                        .titled(u'Subsite')
                        .with_language('fr')
                        .having(link_site_in_languagechooser=True))
        introduce_language_subsites(german, french)

        folder = create(Builder('folder').within(german))

        langs = getMultiAdapter((folder, self.request), ILanguages)
        self.assertEquals(
            [{'url': self.portal.absolute_url(),
              'title': u'English',
              'code': 'en'},

             {'url': french.absolute_url(),
              'title': u'Fran\xe7ais',
              'code': 'fr'}],

            langs.get_related_languages())

    def test_related_languages_is_inherited_from_site_root(self):
        german = create(Builder('subsite')
                        .titled(u'Subsite')
                        .with_language('de')
                        .having(link_site_in_languagechooser=True))
        french = create(Builder('subsite')
                        .titled(u'Subsite')
                        .with_language('fr')
                        .having(link_site_in_languagechooser=True))

        folder = create(Builder('folder'))

        langs = getMultiAdapter((folder, self.request), ILanguages)
        self.assertEquals(
            [{'url': german.absolute_url(),
              'title': u'Deutsch',
              'code': 'de'},

             {'url': french.absolute_url(),
              'title': u'Fran\xe7ais',
              'code': 'fr'}],

            langs.get_related_languages())
