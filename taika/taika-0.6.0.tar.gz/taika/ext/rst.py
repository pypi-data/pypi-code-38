"""
:mod:`taika.ext.rst` -- ReStructuredText
========================================

This extension parses the content of the documents into HTML using ReStructuredText specifications.

Trigger
-------

This extension is subscribed to the "doc-post-read" event.

Frontmatter
-----------

None.

Process
-------

#. Reads the suffix of `path` and if it matches, process the document.
#. Modifies the suffix of `url` path to ".html".
#. Process the content with :func:`docutils.publish_parts` and replaces it with the "body" part.
#. Done!

Configuration
-------------

.. data:: rst_suffix (list)

    Default: **[.rst]**

    Tells the parser to ONLY modify docs with that suffix. Otherwise the document is ignored.
    This is checked against the source path (`path`), not the destination path (`url`).

.. data:: rst_strict (bool)

    Default: **True**

    Exits with error code 1 if there is any warning or error when parsing files.


.. data:: rst_options (dict)

    Default:
        | stylesheet_path: ''
        | halt_level: 1
        | traceback: True
        | report_level: 5
        | syntax_highlight: 'short'
        | doctitle_xform: False

    You can check the available options at `HTML writer documentation
    <http://docutils.sourceforge.net/docs/user/config.html#html4css1-writer>`_


Functions
---------
"""
import logging
import sys
from io import StringIO

try:
    from docutils.core import publish_parts
    from docutils.utils import SystemMessage
except ImportError:
    print("'taika.ext.rst' needs the package 'docutils' to be installed.")
    sys.exit(1)


RST_OPTIONS = {
    "stylesheet_path": "",
    "halt_level": 1,
    "traceback": True,
    "report_level": 5,
    "syntax_highlight": "short",
    "doctitle_xform": False,
}
DEFAULT_SUFFIX = ".rst"
OUT_SUFFIX = ".html"
RST_STRICT = True

LOGGER = logging.getLogger(__name__)


def parse_rst(site, document):
    """Parse ``content`` and modify ``url`` keys of `document`.

    Parameters
    ----------
    site : :class:`taika.taika.Taika`
        The Taika site.
    document : dict
        The document to be parsed.
    """
    suffixes = site.config.get("rst_suffix", DEFAULT_SUFFIX)
    rst_options = site.config.get("rst_options", RST_OPTIONS)

    if document["path"].suffix not in suffixes:
        return

    document["url"] = document["url"].with_suffix(OUT_SUFFIX)
    warning_stream = StringIO()
    rst_options["warning_stream"] = warning_stream
    try:
        html = publish_parts(
            source=document["content"],
            source_path=site.source / document["path"],
            writer_name="html5",
            settings_overrides=rst_options,
        )["body"]

        document["content"] = html
    except SystemMessage:
        msg = warning_stream.getvalue().strip("\n").replace("\n", " ")
        rst_strict = site.config.get("rst_strict", RST_STRICT)
        if rst_strict:
            action = "Exiting"
            LOGGER.critical(f"Problem when parsing a file. Error message: '{msg}' {action}...")
            sys.exit(1)
        else:
            action = f"Skipping, 'rst_strict' = {rst_strict}"
            LOGGER.warning(f"Problem when parsing a file. Error message: '{msg}' {action}...")


def setup(site):
    site.events.register("doc-post-read", parse_rst)
