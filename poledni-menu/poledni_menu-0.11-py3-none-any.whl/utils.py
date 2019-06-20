import urllib.request

import lxml.html


def killwhitespace(string):
    """ Merge consecutive spaces into one space. """
    return " ".join(s.strip() for s in string.split())


def parsed_html_doc(url):
    """ Retrieve HTML document from the URL. Cache results for same URL. """
    if not hasattr(parsed_html_doc, "cache"):
        parsed_html_doc.cache = dict()
    if url not in parsed_html_doc.cache:
        parsed_html_doc.cache[url] = lxml.html.parse(
            urllib.request.urlopen(url),
        )
    return parsed_html_doc.cache[url]
