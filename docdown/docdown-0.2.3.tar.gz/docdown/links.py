# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals, print_function

from markdown.inlinepatterns import LinkPattern, LINK_RE
from markdown.extensions import Extension


class DocDownLinkPattern(LinkPattern):

    def __init__(self, link_map=None, **kwargs):
        self.link_map = link_map or {}
        super(DocDownLinkPattern, self).__init__(**kwargs)

    def sanitize_url(self, url):
        if '#' in url:
            uri, uri_hash = url.split('#', 1)
        else:
            uri = url
            uri_hash = ''

        if uri in self.link_map:
            uri = self.link_map.get(uri)

        if uri_hash:
            uri = u'%s#%s' % (uri, uri_hash)
        return super(DocDownLinkPattern, self).sanitize_url(uri)


class LinksExtension(Extension):

    def __init__(self, **kwargs):
        self.config = {
            'link_map': [{}, 'Dict mapping source urls to target urls.'],
        }
        super(LinksExtension, self).__init__(**kwargs)

    def extendMarkdown(self, md, md_globals):
        link_map = self.getConfig('link_map')
        md.inlinePatterns['link'] = DocDownLinkPattern(link_map=link_map, pattern=LINK_RE, markdown_instance=md)


def makeExtension(*args, **kwargs):
    return LinksExtension(*args, **kwargs)
