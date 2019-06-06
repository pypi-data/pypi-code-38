try:
    from html import unescape
except ImportError:
    from HTMLParser import HTMLParser  # type: ignore

    unescape = HTMLParser().unescape

try:
    from lxml import etree
except ImportError:
    try:
        import xml.etree.cElementTree as etree  # type: ignore
    except ImportError:
        import xml.etree.ElementTree as etree  # type: ignore

try:
    import typing
except ImportError:
    typing = None  # type: ignore
