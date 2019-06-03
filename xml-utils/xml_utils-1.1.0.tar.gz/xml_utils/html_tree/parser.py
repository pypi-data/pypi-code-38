""" Package parsing HTML
"""
from lxml import etree, html
from lxml.html.diff import htmldiff
from xml_utils.commons.exceptions import HTMLError
from xml_utils.xsd_tree.xsd_tree import XSDTree


def parse_html(html_text, parent_tag=''):
    """ Try to parse and unparse HTML to verify that is correctly formatted

    Params:
        html_text:
        parent_tag:

    Returns:

    Raises:
    """
    try:
        return XSDTree.fromstring("<%s>%s</%s>" % (parent_tag, html_text, parent_tag))
    except Exception as e:
        raise HTMLError(e.message)


def safe_html(html_text):
    """ Returns safe HTML from input

    Parameters:
        html_text:

    Returns:
    """
    return html.tostring(html.fragment_fromstring(html_text, create_parent='div'))


def from_string(html_content, base_url=None, parser=None, **kw):
    """
    Parse the html, returning a single element/document.

    This tries to minimally parse the chunk of text, without knowing if it
    is a fragment or a document.

    base_url will set the document's base_url attribute (and the tree's docinfo.URL)

    Params:
        html_content:
        base_url:
        parser:

    Returns:
    """
    return html.fromstring(html_content, base_url, parser, **kw)


def to_string(doc, pretty_print=False, include_meta_content_type=False,
             encoding=None, method="html", with_tail=True, doctype=None):
    """Return an HTML string representation of the document.

    Parameters:
        doc:
        pretty_print:
        include_meta_content_type:
        encoding:
        method:
        with_tail:
        doctype:

    Returns:
    """
    return html.tostring(doc, pretty_print, include_meta_content_type, encoding, method,
                         with_tail, doctype)


def html_diff(old_html, new_html):
    """ Do a diff of the old and new document.  The documents are HTML
    *fragments* (str/UTF8 or unicode), they are not complete documents
    (i.e., no <html> tag).
    """
    return htmldiff(old_html, new_html)
