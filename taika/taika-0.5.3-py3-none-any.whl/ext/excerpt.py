"""
:mod:`taika.ext.excerpt` -- Documents excerpts
==============================================

This extensions creates a excerpt for the documents based on it's content.

Event
-----

This extension is subscribed to the "doc-post-read" event.

Frontmatter
-----------

.. data:: excerpt_separator (str)

    Use this separator instead of the global separator defined in the configuration.

Configuration
-------------

.. code-block:: yaml

    excerpt_separator: <!-- read-more -->


.. data:: excerpt_separator (str)

    Default: :code:`None`

    A string that will be used as excerpt separator. Default to :code:`None` so no excerpt
    will be generated.


Process
-------

#. Check for the frontmatter option, otherwise use the global or the default separator.
#. If separator is None, the first :code:`<p>` tag is retrieved if existent.
#. If the first :code:`<p>` tag is not found, :code:`\\n\\n` (double line separator) is
   used as separator.
#. If separator is something, the text before that separator is retrieved if existent.
#. The :code:`excerpt` is inserted into the document so it will be accessible.

Classes and Functions
---------------------
"""
import logging
import sys

try:
    import bs4
except ImportError:
    print("taika.ext.excerpt needs beautifulsoup4 to be installed.")
    sys.exit(1)

DEFAULT_SEPARATOR = None
LOGGER = logging.getLogger(__name__)


def get_excerpt(site, document):
    separator = site.config.get("excerpt_separator", DEFAULT_SEPARATOR)
    if document["url"].suffix != ".html":
        LOGGER.debug(f"Document {document['url']} doesn't finish in html.")
        return

    if "excerpt_separator" in document:
        separator = document["excerpt_separator"]

    if separator is None:
        html = bs4.BeautifulSoup(document["content"], features="html.parser")
        first_p = html.find("p")

        if first_p is not None:
            document["excerpt"] = "<p>" + first_p.get_text() + "</p>"
            LOGGER.debug(f"Extracting the first paragraph for {document['url']}.")
        else:
            LOGGER.debug(f" Didn't found <p> tag. Using \\n\\n as separator.")
            document["excerpt"] = _text_before("\n\n", document["content"])
    else:
        LOGGER.debug(f"Using separator '{separator}' for document {document['url']}.")
        document["excerpt"] = _text_before(separator, document["content"])


def _text_before(string, text):
    pos = text.find(string)
    if pos == -1:
        LOGGER.debug(f"Separator {string} not found on text.")
        LOGGER.debug(text)

    return text[:pos]


def setup(site):
    site.events.register("doc-post-read", get_excerpt)
