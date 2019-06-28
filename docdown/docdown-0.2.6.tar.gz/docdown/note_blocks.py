# -*- coding: utf-8 -*-

"""
note_blocks
----------------------------------

docdown.note_blocks Markdown extension module
"""

from __future__ import absolute_import, unicode_literals, print_function

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
import re

from .docdown import TemplateRenderMixin


DEFAULT_ADAPTER = 'docdown.template_adapters.StringFormatAdapter'


class NoteBlockPreprocessor(TemplateRenderMixin, Preprocessor):

    RE = re.compile(r'''
(?P<fence>^(?:!{3,}))\W(?P<type>\w+)\W*\n
(?P<content>.*?)(?<=\n)
(?P=fence)[ ]*$''', re.MULTILINE | re.DOTALL | re.VERBOSE)

    def __init__(self, prefix='', postfix='', tags=None, template_adapter=DEFAULT_ADAPTER, default_tag='', **kwargs):
        if tags is None:
            tags = {}
        self.prefix = prefix
        self.postfix = postfix
        self.tags = tags
        self.default_tag = default_tag
        super(NoteBlockPreprocessor, self).__init__(template_adapter=template_adapter, **kwargs)

    def run(self, lines):
        text = "\n".join(lines)
        renderer = self.get_template_adapter()
        while 1:
            m = self.RE.search(text)
            if m:
                fence_type = m.group('type')
                css_class = fence_type.lower()
                content = m.group('content')

                try:
                    context = self.tags[css_class]
                except KeyError:
                        css_class = self.default_tag
                        context = self.tags.get(css_class, {})

                context.update({'tag': css_class})

                prefix_template = context.get('prefix', self.prefix)
                postfix_template = context.get('postfix', self.postfix)
                prefix = renderer.render(template=prefix_template, context=context)
                postfix = renderer.render(template=postfix_template, context=context)

                start_tag = self.markdown.htmlStash.store(prefix, safe=True)
                end_tag = self.markdown.htmlStash.store(postfix, safe=True)

                text = '%s\n%s\n\n%s\n%s\n%s' % (text[:m.start()], start_tag, content, end_tag, text[m.end():])
            else:
                break

        return text.split("\n")


class NoteExtension(Extension):
    """
    Renders a block of HTML with a title, svg image, and content to be displayed as a note.
    The svg image is rendered using.

    Configuration Example:
    {
        'template_adapter': 'docdown.template_adapters.StringFormatAdapter',
        'prefix': ('<div class="{ tag }">'
                   '  <div class="icon">'
                   '    {% svg "{ svg }" %}'
                   '    <img class="icon--pdf" src="{% static "{ svg_path }" %}"'
                   '  </div>'
                   '  <h5>{ title }</h5>'
                   '</div>'),
        'postfix': '</div>',
        'tags': {
            'tag_name': {
                'svg': 'standard/icon-must',
                'svg_path': 'svg/standard/icon-must.svg',
                'title': 'Must'
            },
        }
    }
    """

    def __init__(self, **kwargs):
        self.config = {
            'prefix': ['<div>', 'Opening tag(s) which wrap the content'],
            'postfix': ['</div>', 'Closing tag(s) which wrap the content'],
            'tags': [{}, 'Template context passed into template rendering'],
            'template_adapter': ['docdown.template_adapters.StringFormatAdapter',
                                 ('Adapter for rendering prefix and postfix templates'
                                  ' using your template language of choice.')],
            'default_tag': ['', 'Default tag to use if the specified tag is not in the tags dict'],
        }
        super(NoteExtension, self).__init__(**kwargs)

    def extendMarkdown(self, md, md_globals):
        """ Add NoteBlockPreprocessor to the Markdown instance. """
        md.registerExtension(self)

        prefix = self.getConfig('prefix')
        postfix = self.getConfig('postfix')
        tags = self.getConfig('tags')
        template_adapter = self.getConfig('template_adapter')
        default_tag = self.getConfig('default_tag')

        md.preprocessors.add('note_blocks',
                             NoteBlockPreprocessor(prefix=prefix,
                                                   postfix=postfix,
                                                   tags=tags,
                                                   template_adapter=template_adapter,
                                                   default_tag=default_tag,
                                                   markdown_instance=md),
                             ">normalize_whitespace")


def makeExtension(*args, **kwargs):
    return NoteExtension(*args, **kwargs)


# TODO: put this in a different module
