# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals, print_function

from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension


class MediaTreeprocessor(Treeprocessor):

    def __init__(self, media_url=None, **kwargs):
        self.media_url = media_url
        super(MediaTreeprocessor, self).__init__(**kwargs)

    def run(self, root):
        image_tags = root.findall('.//img')
        if self.media_url is not None:
            for image_tag in image_tags:
                tag_src = image_tag.get('src')
                if not tag_src.lower().startswith('http') and not tag_src.startswith('//'):
                    if tag_src.startswith('./'):
                        tag_src = tag_src[2:]
                    # TODO: relative image tag source starting with . like sequence
                    # diagrams?

                    # Make sure we don't create a url like http://example.org//something.html
                    # if media_url ends with / and tag_src starts with /
                    # example.com/ + /blah.html = example.com/blah.html
                    # example.com + /blah.html = example.com/blah.html
                    # example.com/ + blah.html = example.com/blah.html
                    # example.com + blah.html = example.com/blah.html
                    # example.com + ./blah.html = example.com/blah.html
                    image_tag.set('src', self.media_url.rstrip('/') + '/' + tag_src.lstrip('/'))


class MediaExtension(Extension):

    def __init__(self, **kwargs):
        self.config = {
            'media_url': ['.', 'Path or URL base for the media'],
        }
        super(MediaExtension, self).__init__(**kwargs)

    def extendMarkdown(self, md, md_globals):
        """ Add MediaTreeprocessor to the Markdown instance. """
        md.registerExtension(self)

        media_url = self.getConfig('media_url')
        md.treeprocessors.add('media', MediaTreeprocessor(media_url=media_url, markdown_instance=md), '>inline')


def makeExtension(*args, **kwargs):
    return MediaExtension(*args, **kwargs)
