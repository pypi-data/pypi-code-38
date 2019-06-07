from __future__ import unicode_literals
from __future__ import absolute_import
import cgi
import re
from types import FunctionType
from io import open

import six
import bleach
import html5lib.filters.sanitizer

# based on allura.lib.utils.ForgeHTMLSanitizerFilter
_form_tags = {'button', 'datalist', 'fieldset', 'form', 'input', 'label', 'legend', 'meter', 'optgroup', 'option',
              'output', 'progress', 'select', 'textarea', }
ALLOWED_TAGS = [
    el[1]  # just the tag name, no namespace
    for el in html5lib.filters.sanitizer.allowed_elements
    if el[0] == html5lib.constants.namespaces['html']
    and el[1] not in _form_tags
]

# copied from html5lib.filters.sanitizer.allowed_attributes but only the HTML ones at tope
# TODO: delineate by tag, instead of '*' for all
# bleach_whitelist.markdown_attrs and .print_attrs has a very short list
# bleach.ALLOWED_ATTRIBUTES is just an example, not realistic
ALLOWED_ATTRIBUTES = {
    '*': [
        el[1] for el in [
            (None, 'abbr'),
            (None, 'accept'),
            (None, 'accept-charset'),
            (None, 'accesskey'),
            (None, 'action'),
            (None, 'align'),
            (None, 'alt'),
            (None, 'autocomplete'),
            (None, 'autofocus'),
            (None, 'axis'),
            (None, 'background'),
            (None, 'balance'),
            (None, 'bgcolor'),
            (None, 'bgproperties'),
            (None, 'border'),
            (None, 'bordercolor'),
            (None, 'bordercolordark'),
            (None, 'bordercolorlight'),
            (None, 'bottompadding'),
            (None, 'cellpadding'),
            (None, 'cellspacing'),
            (None, 'ch'),
            (None, 'challenge'),
            (None, 'char'),
            (None, 'charoff'),
            (None, 'choff'),
            (None, 'charset'),
            (None, 'checked'),
            (None, 'cite'),
            (None, 'class'),
            (None, 'clear'),
            (None, 'color'),
            (None, 'cols'),
            (None, 'colspan'),
            (None, 'compact'),
            (None, 'contenteditable'),
            (None, 'controls'),
            (None, 'coords'),
            (None, 'data'),
            (None, 'datafld'),
            (None, 'datapagesize'),
            (None, 'datasrc'),
            (None, 'datetime'),
            (None, 'default'),
            (None, 'delay'),
            (None, 'dir'),
            (None, 'disabled'),
            (None, 'draggable'),
            (None, 'dynsrc'),
            (None, 'enctype'),
            (None, 'end'),
            (None, 'face'),
            (None, 'for'),
            (None, 'form'),
            (None, 'frame'),
            (None, 'galleryimg'),
            (None, 'gutter'),
            (None, 'headers'),
            (None, 'height'),
            (None, 'hidefocus'),
            (None, 'hidden'),
            (None, 'high'),
            (None, 'href'),
            (None, 'hreflang'),
            (None, 'hspace'),
            (None, 'icon'),
            (None, 'id'),
            (None, 'inputmode'),
            (None, 'ismap'),
            (None, 'keytype'),
            (None, 'label'),
            (None, 'leftspacing'),
            (None, 'lang'),
            (None, 'list'),
            (None, 'longdesc'),
            (None, 'loop'),
            (None, 'loopcount'),
            (None, 'loopend'),
            (None, 'loopstart'),
            (None, 'low'),
            (None, 'lowsrc'),
            (None, 'max'),
            (None, 'maxlength'),
            (None, 'media'),
            (None, 'method'),
            (None, 'min'),
            (None, 'multiple'),
            (None, 'name'),
            (None, 'nohref'),
            (None, 'noshade'),
            (None, 'nowrap'),
            (None, 'open'),
            (None, 'optimum'),
            (None, 'pattern'),
            (None, 'ping'),
            (None, 'point-size'),
            (None, 'poster'),
            (None, 'pqg'),
            (None, 'preload'),
            (None, 'prompt'),
            (None, 'radiogroup'),
            (None, 'readonly'),
            (None, 'rel'),
            (None, 'repeat-max'),
            (None, 'repeat-min'),
            (None, 'replace'),
            (None, 'required'),
            (None, 'rev'),
            (None, 'rightspacing'),
            (None, 'rows'),
            (None, 'rowspan'),
            (None, 'rules'),
            (None, 'scope'),
            (None, 'selected'),
            (None, 'shape'),
            (None, 'size'),
            (None, 'span'),
            (None, 'src'),
            (None, 'start'),
            (None, 'step'),
            (None, 'style'),
            (None, 'summary'),
            (None, 'suppress'),
            (None, 'tabindex'),
            (None, 'target'),
            (None, 'template'),
            (None, 'title'),
            (None, 'toppadding'),
            (None, 'type'),
            (None, 'unselectable'),
            (None, 'usemap'),
            (None, 'urn'),
            (None, 'valign'),
            (None, 'value'),
            (None, 'variable'),
            (None, 'volume'),
            (None, 'vspace'),
            (None, 'vrml'),
            (None, 'width'),
            (None, 'wrap'),
        ]
    ],
}

# html5lib is pretty limited, but ok
# bleach.sanitizer.ALLOWED_STYLES is none
# bleach_whitelist.all_styles allows way too much, for safety (-moz-binding) or for limiting presentation (position)
ALLOWED_STYLES = html5lib.filters.sanitizer.allowed_css_properties

# less than html5lib.filters.sanitizer.allowed_protocols
# more than bleach.sanitizer.ALLOWED_PROTOCOLS
ALLOWED_PROTOCOLS = ['http', 'https', 'mailto', 'ftp', 'irc', 'ircs', 'nntp', 'sftp']


class Markup(object):

    def __init__(self, *markup_pkgs_or_fns, **markup_extensions):
        # Define markups
        self.markups = []
        for markup_pkg in markup_pkgs_or_fns:
            if type(markup_pkg) == FunctionType:
                self.add_renderer(markup_pkg)
            else:
                renderers = [r for r in dir(markup_pkg) if r.endswith('_markup')]
                for renderer in renderers:
                    func = getattr(markup_pkg, renderer)
                    self.add_renderer(func, markup_extensions)

        self.bleach_cleaner = bleach.Cleaner(
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            styles=ALLOWED_STYLES,
            protocols=ALLOWED_PROTOCOLS,
            strip=False,  # escape unsafe tags instead
            strip_comments=True,
        )

    @property
    def markups_names(self):
        return [m['name'] for m in self.markups]

    def add_renderer(self, func, markup_extensions):
        '''
        Add a function that is responsible for rendering a particular
        markup syntax to HTML.

        The function name should end in \*_markup. The
        function must return a tuple of the pattern used to match supported
        file extensions and a callback to render a string of text.

        The callback recieves one parameter, a Unicode string. It should
        return an HTML representation of that string. Simple callbacks can be
        lambdas, such as creole, textile, or markup.
        '''
        name = func.__name__[:-len('_markup')]

        try:
            ext_pattern, render_fn = func(markup_extensions.get(name))
        except TypeError:
            ext_pattern, render_fn = func()

        self.markups.append(dict(name = name,
                                 ext_pattern = ext_pattern,
                                 render_fn = render_fn,
                            ))

    def render(self, filename, content=None):
        '''
        Provided a filename or a filename and content, render the
        content from a particular markup syntax to HTML. The markup
        syntax is chosen based on matching patterns (e.g., extensions)
        with the filename.
        '''
        if not content:
            with open(filename, 'rb') as f:
                content = f.read()
        content = self.unicode(content)
        (proc, name) = self.renderer(filename)
        if proc:
            html = proc(content)
            return self.unicode(self.bleach_cleaner.clean(html))
        else:
            # make sure unrendered content is at least escaped
            return cgi.escape(content)

    def unicode(self, content):
        '''
        Normalize a variety of encodings into unicode.
        '''
        if type(content) == six.text_type:
            return content
        try:
            content.decode('ascii')
        except UnicodeDecodeError: #pragma: nocover
            # try 2 common encodings
            try:
                content = content.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    content = content.decode('latin_1')
                except UnicodeDecodeError:
                    raise Exception('The content uses an unsupported encoding.')
        return six.text_type(content)

    def can_render(self, filename):
        '''
        Check to see if a particular file is supported. If the file is
        supported, the name of the markup is returned. Otherwise, the
        function returns None.
        '''
        (proc, name) = self.renderer(filename)
        return name

    def renderer(self, filename):
        '''
        Search for any markups that are responsible for the provided
        filename. Returns the function used to render the file and
        the name of the markup.
        '''
        for markup in self.markups:
            if re.search(r"\.(%s)$" % markup['ext_pattern'], filename):
                return markup['render_fn'], markup['name']
        return None, None

from pypeline import markups
markup = Markup(markups)