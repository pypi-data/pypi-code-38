from ftw.contentpage.interfaces import IContentPage
from ftw.topics import _
from ftw.topics.browser.representation import DefaultRepresentation
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class ContentPageRepresentation(DefaultRepresentation):

    template = ViewPageTemplateFile(
        'contentpage_representation.pt')

    def consume(self, objects):
        """Consume all objects left"""

        for obj in objects:
            if IContentPage.providedBy(obj):
                self.objects.append(obj)
            else:
                yield obj

    def title(self):
        return _(u'label_contentpage', default=u'Content pages')

    def position(self):
        return 100
