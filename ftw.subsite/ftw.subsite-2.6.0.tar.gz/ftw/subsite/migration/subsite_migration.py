from ftw.builder import Builder
from ftw.builder import builder_registry
from ftw.builder import create
from ftw.builder import session
from ftw.builder.dexterity import DexterityBuilder
from ftw.simplelayout.contenttypes.behaviors import ITeaser
from ftw.simplelayout.interfaces import IBlockConfiguration
from ftw.simplelayout.interfaces import IPageConfiguration
from plone.app.contenttypes.migration.migration import ATCTFolderMigrator
from plone.app.textfield.value import RichTextValue
from plone.app.uuid.utils import uuidToObject
from plone.i18n.normalizer.interfaces import IFileNameNormalizer
from plone.namedfile.file import NamedBlobImage
from plone.uuid.interfaces import IUUID
from Products.CMFPlone.utils import safe_unicode
from Products.contentmigration.basemigrator.walker import CatalogWalker
from z3c.relationfield import RelationValue
from zope.annotation import IAnnotations
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


class BuilderSession(object):
    auto_commit = False


session.current_session = BuilderSession()


class TextBlockBuilder(DexterityBuilder):
    portal_type = 'ftw.simplelayout.TextBlock'

try:
    # Plone reload support
    builder_registry.register('sl textblock', TextBlockBuilder)
except ValueError:
    pass


class FtwSubsiteMigrator(ATCTFolderMigrator):

    src_portal_type = 'Subsite'
    src_meta_type = 'Subsite'
    dst_portal_type = 'ftw.subsite.Subsite'
    dst_meta_type = None  # not used

    def beforeChange_language_reference(self):
        language_reference_uids = self.old.getRawLanguage_references()
        if language_reference_uids:
            setattr(self.old,
                    '_language_reference_uids',
                    language_reference_uids)

    def migrate_prepare_page_state(self):
        config = IPageConfiguration(self.new)

        page_config = {
            "default": [
                {"cols": [
                    {"blocks": []},
                    {"blocks": []},
                    {"blocks": []},
                    {"blocks": []},
                ]},
                {"cols": [
                    {"blocks": []},
                    {"blocks": []}]
                 }]}
        config.store(page_config)

    def migrate_subsite_fields(self):
        self.new.additional_css = self.old.getAdditional_css()
        self.new.link_site_in_languagechooser = \
            self.old.getField('linkSiteInLanguagechooser').get(self.old)
        self.new.force_language = self.old.getForcelanguage()
        self.new.from_name = self.old.getFromName()
        self.new.from_email = self.old.getFromEmail()

        old_logo = self.old.getField('logo').get(self.old)
        if old_logo.data == '':
            return
        filename = safe_unicode(old_logo.filename)
        normalizer = getUtility(IFileNameNormalizer).normalize
        namedblobimage = NamedBlobImage(data=old_logo.data,
                                        filename=normalizer(filename).decode('utf-8'))
        self.new.logo = namedblobimage

    def migrate_language_references(self):
        # Check restore_language_reference method in migration.py for internal
        # references.
        if hasattr(self.old, '_language_reference_uids'):
            setattr(self.new,
                    '_language_reference_uids',
                    self.old._language_reference_uids)

    def migrate_static_text_portlets_to_textblock(self):
        annotations = IAnnotations(self.old)
        portlets = annotations.get('plone.portlets.contextassignments', None)
        if portlets is None:
            return

        managers = ['ftw.subsite.front1', 'ftw.subsite.front2',
                    'ftw.subsite.front3', 'ftw.subsite.front4',
                    'ftw.subsite.front5', 'ftw.subsite.front6',
                    'ftw.subsite.front7']

        for manager in managers:
            for portlet in portlets.get(manager, {}).values():
                if portlet.__module__ == 'ftw.subsite.portlets.teaserportlet':
                    self.create_block(portlet, manager, 'teaser')
                elif portlet.__module__ == 'plone.portlet.static.static':
                    self.create_block(portlet, manager, 'static')
                else:
                    pass

    def create_block(self, portlet, manager, type_):

        config = IPageConfiguration(self.new)
        normalizer = getUtility(IFileNameNormalizer).normalize
        if type_ == 'teaser':
            block = create(Builder('sl textblock')
                           .within(self.new)
                           .titled(portlet.teasertitle)
                           .having(text=RichTextValue(portlet.teaserdesc),
                                   image=NamedBlobImage(
                                       filename=normalizer(
                                           portlet.image.filename).decode('utf-8'),
                                       data=portlet.image.data)))

            blockconfig = IBlockConfiguration(block)
            blockconfigdata = blockconfig.load()
            blockconfigdata['scale'] = 'large'
            blockconfigdata['imagefloat'] = 'no-float'
            blockconfig.store(blockconfigdata)

            if portlet.internal_target:
                teaser = ITeaser(block)
                target = uuidToObject(portlet.internal_target)
                if target:
                    intids = getUtility(IIntIds)
                    teaser.internal_link = RelationValue(intids.getId(target))

        elif type_ == 'static':
            block = create(Builder('sl textblock')
                           .within(self.new)
                           .titled(portlet.header)
                           .having(text=RichTextValue(portlet.text)))
        else:
            return

        uid = IUUID(block)

        page_state = config.load()
        if manager == 'ftw.subsite.front1':
            page_state['default'][0]['cols'][0]['blocks'].append({'uid': uid})
        elif manager == 'ftw.subsite.front2':
            page_state['default'][0]['cols'][1]['blocks'].append({'uid': uid})
        elif manager == 'ftw.subsite.front3':
            page_state['default'][0]['cols'][2]['blocks'].append({'uid': uid})
        elif manager == 'ftw.subsite.front4':
            page_state['default'][0]['cols'][3]['blocks'].append({'uid': uid})
        elif manager == 'ftw.subsite.front5':
            page_state['default'][1]['cols'][0]['blocks'].append({'uid': uid})
        elif manager == 'ftw.subsite.front6':
            page_state['default'][1]['cols'][1]['blocks'].append({'uid': uid})
        # Don't know where manager 7 belongs
        elif manager == 'ftw.subsite.front7':
            page_state['default'][1]['cols'][0]['blocks'].append({'uid': uid})

        config.store(page_state)


def migrate(portal, migrator):
    """return a CatalogWalker instance in order
    to have its output after migration"""
    walker = CatalogWalker(portal, migrator)()
    return walker


def subsite_migrator(portal):
    return migrate(portal, FtwSubsiteMigrator)
