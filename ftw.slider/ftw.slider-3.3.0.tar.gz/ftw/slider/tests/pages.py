from ftw.testing import browser
from ftw.testing.pages import Plone


class ContentMenu(Plone):

    @property
    def content_views_links(self):
        return browser().find_by_css('#content-views a')

    @property
    def content_views_labels(self):
        return map(lambda link: link.text.strip(), self.content_views_links)

    @property
    def content_actions_labels(self):
        items = browser().find_by_css('#plone-contentmenu-actions dd a')
        return map(lambda link: link.text.strip(), items)

    @property
    def addable_types_links(self):
        nodes = browser().find_by_css('#plone-contentmenu-factories li a')
        return dict([(node.text.strip(), node) for node in nodes])

    @property
    def addable_types_labels(self):
        return self.addable_types_links.keys()
