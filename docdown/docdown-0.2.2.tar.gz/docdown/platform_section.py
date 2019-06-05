# -*- coding: utf-8 -*-

"""
platform_section
----------------------------------

docdown.platform_section Markdown extension module
"""

from __future__ import absolute_import, print_function, unicode_literals

import re

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor


class PlatformSectionPreprocessor(Preprocessor):

    RE = re.compile(r'''
^@!\[(?P<sections>[\w, ]+)\]\W*\n
(?P<content>.*?)(?<=\n)
!@\W*$''', re.MULTILINE | re.DOTALL | re.VERBOSE)

    def __init__(self, platform_section, **kwargs):
        self.platform_section = platform_section.lower().strip()
        super(PlatformSectionPreprocessor, self).__init__(**kwargs)

    def run(self, lines):
        text = "\n".join(lines)
        while 1:
            m = self.RE.search(text)
            if m:
                sections = [section.lower().strip() for section in m.group('sections').split(',')]

                content = m.group('content')

                if self.platform_section in sections:
                    text = '%s\n%s\n%s' % (text[:m.start()], content, text[m.end():])
                else:
                    text = '%s\n%s' % (text[:m.start()], text[m.end():])
            else:
                break

        return text.split("\n")


class PlatformSectionExtension(Extension):
    """
    Renders a block of content if and only if the configured platform section is in the DocDown tag's list of platform
    sections.

    Configuration Example:
    {
        'platform_section': 'Android',
    }
    """

    def __init__(self, **kwargs):
        self.config = {
            'platform_section': ['', 'The platform section that should be rendered.'],
        }
        super(PlatformSectionExtension, self).__init__(**kwargs)

    def extendMarkdown(self, md, md_globals):
        """ Add NoteBlockPreprocessor to the Markdown instance. """
        md.registerExtension(self)

        platform_section = self.getConfig('platform_section')

        md.preprocessors.add('platform_sections',
                             PlatformSectionPreprocessor(
                                platform_section=platform_section,
                                markdown_instance=md),
                             ">normalize_whitespace")


def makeExtension(*args, **kwargs):
    return PlatformSectionExtension(*args, **kwargs)
