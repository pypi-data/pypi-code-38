from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ftw.topics.interfaces import IBackReferenceCollector
from ftw.topics.interfaces import ITopic
from ftw.topics.interfaces import ITopicReferencePresentation
from plone.app.layout.viewlets import ViewletBase
from zope.component import getAdapters
from zope.component import getMultiAdapter


class TopicListing(object):

    listing_template = ViewPageTemplateFile('templates/topic_listing.pt')

    def __init__(self):
        self.sections = None
        self.objects = None
        self.representations = None

    def render_topic_listing(self):
        self.sections, self.objects = self._get_sections_and_objects()
        self.representations = self._get_representations()

        return self.listing_template()

    def get_child_topics(self):
        query = {'object_provides': ITopic.__identifier__,
                 'path': {'query': '/'.join(self.context.getPhysicalPath()),
                          'depth': 1},
                 'sort_on': 'sortable_title'}

        catalog = getToolByName(self.context, 'portal_catalog')
        return catalog(query)

    def has_multiple_sections(self):
        collector = getMultiAdapter((self.context, self.request),
                                    IBackReferenceCollector)

        return len(collector.get_sections()) > 1

    def topic_or_similar_topic_has_brefs(self):
        for section in self.sections:
            if len(section.get('objects')) > 0:
                return True
        return False

    def display_section_headings(self):
        return self.has_multiple_sections() and \
            self.topic_or_similar_topic_has_brefs()

    def _get_representations(self):
        adapters = dict(getAdapters((self.context, self.request),
                                     ITopicReferencePresentation)).values()

        adapters.sort(key=lambda adapter: adapter.position())

        objects = self.objects
        for adapter in adapters:
            objects = adapter.consume(objects)

        return adapters

    def _get_sections_and_objects(self):
        collector = getMultiAdapter((self.context, self.request),
                                    IBackReferenceCollector)
        sections = collector()
        if not sections:
            return [], []

        section = self._get_selected_section(sections)
        section['selected'] = True

        section['objects'].sort(key=lambda obj: obj.Title())

        return (sections, section['objects'])

    def _get_selected_section(self, sections):
        selected_section = self.request.get('section', None)
        for section in sections:
            if section.get('UID') == selected_section:
                return section

        return self._get_current_section(sections)

    def _get_current_section(self, sections):
        sections_by_path = dict(map(lambda item: (item.get('path'), item),
                                    sections))
        path = '/'.join(self.context.getPhysicalPath())

        # Select all sections where the current context is in.
        # This may be multiple sections if nested.
        parental_section_paths = [spath for spath in sections_by_path.keys()
                                  if path.startswith(spath)]

        # Sort the paths by length and pick the longest one, this is
        # the nearest parent.
        section_path = sorted(parental_section_paths,
                              key=len, reverse=True)[0]
        return sections_by_path[section_path]


class TopicView(BrowserView, TopicListing):

    def __init__(self, *args, **kwargs):
        BrowserView.__init__(self, *args, **kwargs)
        TopicListing.__init__(self)

    def subtopics(self):
        return self.render_topic_listing()


class SimplelayoutTopicListingViewlet(ViewletBase, TopicListing):

    def __init__(self, *args, **kwargs):
        ViewletBase.__init__(self, *args, **kwargs)
        TopicListing.__init__(self)

    def render(self):
        return self.render_topic_listing()
