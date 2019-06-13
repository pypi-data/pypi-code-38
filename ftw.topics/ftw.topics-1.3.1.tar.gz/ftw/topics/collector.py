from Acquisition import aq_inner
from copy import deepcopy
from DateTime import DateTime
from ftw.topics.interfaces import IBackReferenceCollector
from ftw.topics.interfaces import ITopic
from operator import attrgetter
from plone import api
from plone.app.dexterity.behaviors.metadata import IPublication
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.dexterity.interfaces import IDexterityContent
from plone.memoize import instance
from Products.Archetypes.interfaces.referenceable import IReferenceable
from Products.CMFCore.utils import getToolByName
from zc.relation.interfaces import ICatalog
from zope.component import adapts
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.interface import implements
from zope.interface import Interface
from zope.intid.interfaces import IIntIds


class DefaultCollector(object):
    implements(IBackReferenceCollector)
    adapts(ITopic, Interface)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.group_by = INavigationRoot
        self.mtool = getToolByName(self.context, 'portal_membership')

    def __call__(self, group_by=INavigationRoot):
        self.group_by = group_by
        return self._get_brefs_per_section()

    @instance.memoize
    def get_sections(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        site = getSite()

        result = [{'label': site.Title(),
                   'path': '/'.join(site.getPhysicalPath()),
                   'UID': 'root',
                   'objects': []}]

        def brain_to_item(brain):
            return {'label': brain.Title,
                    'path': brain.getPath(),
                    'UID': brain.UID,
                    'objects': []}

        brains = catalog(object_provides=self.group_by.__identifier__)
        result.extend(map(brain_to_item, brains))
        self._mark_current_section(result)
        return result

    def _mark_current_section(self, sections):
        sections_by_path = sorted(sections,
                                  key=lambda section: section['path'],
                                  reverse=True)

        current_path = '/'.join(self.context.getPhysicalPath())
        for section in sections_by_path:
            if current_path.startswith(section['path']):
                section['is_current_section'] = True
                return

    def _get_brefs_per_section(self):
        """Returns all back references per section.
        """

        section_paths = sorted(
            map(lambda sec: sec['path'], self.get_sections()),
            key=len, reverse=True)

        mapping = dict(map(lambda path: (path, []), section_paths))
        for obj in self._get_merged_brefs():
            path = '/'.join(obj.getPhysicalPath())
            possible_sec_paths = [spath for spath in section_paths
                                  if path.startswith(spath)]

            # use the longest section path
            spath = sorted(possible_sec_paths, key=len, reverse=True)[0]
            mapping[spath].append(obj)

        result = []
        for section in map(deepcopy, self.get_sections()):
            if mapping[section['path']]:
                section['objects'] = mapping[section['path']]
                result.append(section)

            elif section.get('is_current_section'):
                result.append(section)

        return result

    def _get_merged_brefs(self):
        """Returns all backrefrences to the current context and its
        similar topic objects (see _get_similar_topic_objects docstring).
        """
        unrestricted_objects = reduce(
            list.__add__,
            map(self._get_brefs_for,
                self._get_similar_topic_objects()))

        return filter(
            self._filter_view_permission, unrestricted_objects)

    def _filter_view_permission(self, obj):
        if self.mtool.checkPermission('View', obj):
            return obj

    def _get_similar_topic_objects(self):
        """Returns all objects which have the same relative path to the
        nearest parent providing self.group_by (INavigationRoot by default)
        as the current context.
        The current context is included.
        """
        topic_path = '/'.join(self.context.getPhysicalPath())

        section_paths = sorted(map(lambda item: item.get('path'),
                                   self.get_sections()),
                               key=len, reverse=True)
        section_path = [spath for spath in section_paths
                        if topic_path.startswith(spath)][0]

        # path of context relative to next subsite or site root
        relative_path = topic_path.replace(section_path + '/', '', 1)

        # possibile similar paths
        similar_paths = map(lambda path: '/'.join((path, relative_path)),
                            section_paths)

        # similar brains, including the current context
        query = {'path': {'query': similar_paths,
                          'depth': 0}}
        catalog = getToolByName(self.context, 'portal_catalog')
        return map(lambda brain: brain.getObject(), catalog(query))

    def _get_brefs_for(self, obj):
        objs = self._get_at_brefs_for(obj) + self._get_dx_brefs_for(obj)
        return filter(self._filter_inactive_content, objs)

    def _get_at_brefs_for(self, obj):
        return IReferenceable(obj).getBRefs()

    def _get_dx_brefs_for(self, obj):
        catalog = getUtility(ICatalog)
        obj_intid = getUtility(IIntIds).getId(aq_inner(obj))
        relations = catalog.findRelations({'to_id': obj_intid})
        return map(attrgetter('from_object'), relations)

    def _filter_inactive_content(self, obj):
        if IDexterityContent.providedBy(obj):
            effective_date, expiration_date = self._get_dx_publication_dates(obj)
        else:
            effective_date, expiration_date = self._get_at_publication_dates(obj)

        if not effective_date and not expiration_date:
            return True

        now = DateTime()

        if not api.user.has_permission('Access inactive portal content') and expiration_date:
            if now > expiration_date:
                return False

        if not api.user.has_permission('Access future portal content') and effective_date:
            if now < effective_date:
                return False

        return True

    def _get_at_publication_dates(self, obj):
        return obj.getEffectiveDate(), obj.getExpirationDate()

    def _get_dx_publication_dates(self, obj):
        publication = IPublication(obj, None)
        if not publication:  # IPublication is not supported
            return None, None

        effective = publication.effective
        expiration = publication.expires

        # convert from datetime to DateTime as used by archetypes
        return DateTime(effective) if effective else None, \
            DateTime(expiration) if expiration else None
