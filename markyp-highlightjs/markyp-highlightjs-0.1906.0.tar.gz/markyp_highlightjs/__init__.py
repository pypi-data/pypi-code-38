"""
Components for adding syntax highlighting to a `markyp-html` webpage using Highlight.js.

See https://www.npmjs.com/package/highlight.js.
"""

from typing import Optional, Tuple

from markyp import PropertyValue
from markyp_html import link, script
from markyp_html.block import pre
from markyp_html.inline import code as html_code


__author__ = "Peter Volf"
__copyright__ = "Copyright 2019, Peter Volf"
__email__ = "do.volfp@gmail.com"
__license__ = "MIT"
__url__ = "https://github.com/volfpeter/markyp-highlightjs"
__version__ = "0.1906.0"


__all__ = (
    "CDN", "js", "themes", "highlight",
    "bash", "css", "html", "javascript", "json", "markdown", "python", "sql", "xml"
)


class CDN(object):
    """
    CDN information for Highlight.js.
    """

    __slots__ = ()

    CDN_URL: str = "https://cdnjs.cloudflare.com/ajax/libs/highlight.js"

    VERSION: str = "9.15.6"

    @classmethod
    def cdn_url_with_version(cls) -> str:
        """
        Returns the concatenated value of `CDN_URL` and `VERSION`.
        """
        return f"{cls.CDN_URL}/{cls.VERSION}"

    @classmethod
    def url_for_js(cls) -> str:
        """
        Returns the CDN URL for Highlight.js.
        """
        return f"{cls.cdn_url_with_version()}/highlight.min.js"

    @classmethod
    def url_for_style(cls, style_name: str) -> str:
        """
        Returns the CDN URL for the CSS style with the given name.

        Arguments:
            style_name: The name of the Highlight.js style to get the
                        CDN URL for.
        """
        return f"{cls.cdn_url_with_version()}/styles/{style_name}.min.css"


class __JavaScript(object):
    """
    JavaScript `script` elements of Highlight.js.
    """

    __slots__ = ()

    @property
    def js_import(self) -> script:
        """
        Highlight.js JavaScript import element.
        """
        return script.ref(CDN.url_for_js())

    @property
    def js_init(self) -> script:
        """
        Script element that initializes Highlight.js on the page. This script must be placed
        _after_ the Highlight.js import (`js_import` element here) in the markup.
        """
        return script("hljs.initHighlightingOnLoad();")

    @property
    def js(self) -> Tuple[script, script]:
        """
        A tuple of `script` elements: the first imports Highlight.js and the second initializes it.
        """
        return (self.js_import, self.js_init)


class __Themes(object):
    """
    Highlight.js themes for syntax highlighting.
    """

    __slots__ = ()

    @property
    def atom_one_dark(self) -> link:
        """
        Atom One Dark theme CSS link.
        """
        return link.css(CDN.url_for_style("atom-one-dark"))

    @property
    def atom_one_light(self) -> link:
        """
        Atom One Light theme CSS link.
        """
        return link.css(CDN.url_for_style("atom-one-light"))

    @property
    def darcula(self) -> link:
        """
        Darcula theme CSS link.
        """
        return link.css(CDN.url_for_style("darcula"))

    @property
    def default(self) -> link:
        """
        Default theme CSS link.
        """
        return link.css(CDN.url_for_style("default"))

    @property
    def github(self) -> link:
        """
        GitHub theme CSS link.
        """
        return link.css(CDN.url_for_style("github"))

    @property
    def github_gist(self) -> link:
        """
        GitHub gist theme CSS link.
        """
        return link.css(CDN.url_for_style("github-gist"))

    @property
    def idea(self) -> link:
        """
        Idea theme CSS link.
        """
        return link.css(CDN.url_for_style("idea"))

    @property
    def monokai(self) -> link:
        """
        Monokai theme CSS link.
        """
        return link.css(CDN.url_for_style("monokai"))

    @property
    def solarized_dark(self) -> link:
        """
        Solarized Dark theme CSS link.
        """
        return link.css(CDN.url_for_style("solarized-dark"))

    @property
    def solarized_light(self) -> link:
        """
        Solarized Light theme CSS link.
        """
        return link.css(CDN.url_for_style("solarized-light"))


js: __JavaScript = __JavaScript()
"""
JavaScript `script` elements of Highlight.js.
"""


themes: __Themes = __Themes()
"""
Highlight.js themes for syntax highlighting.
"""

# -- Generic highligher methods
# -----------------------------------------------------------------------------


def highlight(code: str, *, language: str, class_: Optional[str] = None, **kwargs: PropertyValue) -> pre:
    """
    Higher order component that creates a `<pre><code class="{language}">{code}</code></pre>`
    HTML segment that Highlight.js will automatically highlight.

    Keyword arguments not listed in the arguments section are turned into element
    attributes on the created `pre` element.

    Arguments:
        code: The actual code to highlight.
        language: The name of the programming language, see https://highlightjs.org/static/demo/.
        class_: CSS classes to add to the created `pre` element.
    """
    return pre(html_code(code, class_=language), class_=class_, **kwargs)


# -- Language-specific highligher methods
# -----------------------------------------------------------------------------


def bash(code: str, *, class_: Optional[str] = None, **kwargs: PropertyValue) -> pre:
    """
    Highlighter method for Bash code.

    Keyword arguments not listed in the arguments section are turned into element
    attributes on the created `pre` element.

    Arguments:
        code: The actual code to highlight.
        class_: CSS classes to add to the created `pre` element.
    """
    return highlight(code, language="bash", class_=class_, **kwargs)


def css(code: str, *, class_: Optional[str] = None, **kwargs: PropertyValue) -> pre:
    """
    Highlighter method for CSS code.

    Keyword arguments not listed in the arguments section are turned into element
    attributes on the created `pre` element.

    Arguments:
        code: The actual code to highlight.
        class_: CSS classes to add to the created `pre` element.
    """
    return highlight(code, language="css", class_=class_, **kwargs)


def html(code: str, *, class_: Optional[str] = None, **kwargs: PropertyValue) -> pre:
    """
    Highlighter method for HTML code.

    Keyword arguments not listed in the arguments section are turned into element
    attributes on the created `pre` element.

    Arguments:
        code: The actual code to highlight.
        class_: CSS classes to add to the created `pre` element.
    """
    return highlight(code, language="html", class_=class_, **kwargs)


def javascript(code: str, *, class_: Optional[str] = None, **kwargs: PropertyValue) -> pre:
    """
    Highlighter method for JavaScript code.

    Keyword arguments not listed in the arguments section are turned into element
    attributes on the created `pre` element.

    Arguments:
        code: The actual code to highlight.
        class_: CSS classes to add to the created `pre` element.
    """
    return highlight(code, language="javascript", class_=class_, **kwargs)


def json(code: str, *, class_: Optional[str] = None, **kwargs: PropertyValue) -> pre:
    """
    Highlighter method for JSON code.

    Keyword arguments not listed in the arguments section are turned into element
    attributes on the created `pre` element.

    Arguments:
        code: The actual code to highlight.
        class_: CSS classes to add to the created `pre` element.
    """
    return highlight(code, language="json", class_=class_, **kwargs)


def markdown(code: str, *, class_: Optional[str] = None, **kwargs: PropertyValue) -> pre:
    """
    Highlighter method for MarkDown code.

    Keyword arguments not listed in the arguments section are turned into element
    attributes on the created `pre` element.

    Arguments:
        code: The actual code to highlight.
        class_: CSS classes to add to the created `pre` element.
    """
    return highlight(code, language="markdown", class_=class_, **kwargs)


def python(code: str, *, class_: Optional[str] = None, **kwargs: PropertyValue) -> pre:
    """
    Highlighter method for Python code.

    Keyword arguments not listed in the arguments section are turned into element
    attributes on the created `pre` element.

    Arguments:
        code: The actual code to highlight.
        class_: CSS classes to add to the created `pre` element.
    """
    return highlight(code, language="python", class_=class_, **kwargs)


def sql(code: str, *, class_: Optional[str] = None, **kwargs: PropertyValue) -> pre:
    """
    Highlighter method for SQL code.

    Keyword arguments not listed in the arguments section are turned into element
    attributes on the created `pre` element.

    Arguments:
        code: The actual code to highlight.
        class_: CSS classes to add to the created `pre` element.
    """
    return highlight(code, language="sql", class_=class_, **kwargs)


def xml(code: str, *, class_: Optional[str] = None, **kwargs: PropertyValue) -> pre:
    """
    Highlighter method for XML code.

    Keyword arguments not listed in the arguments section are turned into element
    attributes on the created `pre` element.

    Arguments:
        code: The actual code to highlight.
        class_: CSS classes to add to the created `pre` element.
    """
    return highlight(code, language="xml", class_=class_, **kwargs)
