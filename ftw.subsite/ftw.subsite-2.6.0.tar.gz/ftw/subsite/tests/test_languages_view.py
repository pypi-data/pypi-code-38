from ftw.builder import Builder
from ftw.builder import create
from ftw.subsite.tests.base import IntegrationTestCase
from z3c.relationfield import RelationValue
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


def introduce_language_subsites(*subsites):
    intids = getUtility(IIntIds)

    for subsite in subsites:
        ids = [intids.getId(obj) for obj in subsites]
        ids.remove(intids.getId(subsite))
        subsite.language_references = [RelationValue(id_) for id_ in ids]


class TestLanguagesView(IntegrationTestCase):

    def setUp(self):
        self.portal = self.layer['portal']

    def test_available_when_subsites_language_referenced(self):
        german = create(Builder('subsite')
                        .titled(u'Subsite DE')
                        .with_language('de'))
        french = create(Builder('subsite')
                        .titled(u'Subsite FR')
                        .with_language('fr'))
        introduce_language_subsites(german, french)
        self.assertTrue(
            german.restrictedTraverse('@@subsite-languages').available())

    def test_not_available_unless_languages_hooked_up(self):
        german = create(Builder('subsite')
                        .titled(u'Subsite DE')
                        .with_language('de'))
        self.assertFalse(
            german.restrictedTraverse('@@subsite-languages').available())

    def test_available_on_site_root_when_subsites_hooked_up(self):
        create(Builder('subsite')
               .titled(u'Subsite DE')
               .with_language('de')
               .having(link_site_in_languagechooser=True))

        self.assertTrue(
            self.portal.restrictedTraverse('@@subsite-languages').available())

    def test_not_available_on_site_root_when_not_hooked_up(self):
        self.assertFalse(
            self.portal.restrictedTraverse('@@subsite-languages').available())
