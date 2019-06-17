"""
Pypeline's built-in markups; use these as examples for how to create your
own markup functions.
"""


from __future__ import unicode_literals
from __future__ import absolute_import

try:
    import creoleparser
except ImportError:
    pass
else:
    def creole_markup():
        return r'creole', lambda s: creoleparser.text2html(s)


try:
    import markdown
except ImportError:
    pass
else:
    def markdown_markup(extensions=None):
        return r'md|mkdn?|mdown|markdown', lambda s: markdown.markdown(s, extensions=extensions or [])

try:
    import textile
except ImportError:
    pass
else:
    def textile_markup():
        return r'textile', lambda s: textile.textile_restricted(s, lite=False, noimage=False)

try:
    from docutils.core import publish_parts
    from docutils.writers.html4css1 import Writer
except ImportError:
    pass
else:
    def rest_markup():
        # see http://docutils.sourceforge.net/docs/howto/security.html
        settings = dict(
            cloak_email_addresses=True,
            file_insertion_enabled=False,
            raw_enabled=False,
            strip_comments=True,
            doctitle_xform=False,
            report_level=5,
        )

        def render(s):
            parts = publish_parts(s, writer=Writer(), settings_overrides=settings)
            if 'html_body' in parts:
                html = parts['html_body']
                return html
            return ''
        return r're?st(\.txt)?', render
