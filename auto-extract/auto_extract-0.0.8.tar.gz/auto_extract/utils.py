import re
from tldextract import tldextract

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin


def extract_domain(url):
    tld = tldextract.extract(url)
    name = ".".join([x for x in tld if x])
    protocol = url.split('//', 1)[0]
    return name, protocol + '//' + name


def extract_links(tree, domain, only_this_domain=True):
    links = tree.xpath("//a/@href")
    links = [urljoin(domain, x) for x in links]
    if only_this_domain:
        links = list(set([x for x in links if domain in x]))
    return links


def extract_headings(tree):
    for h in ["//h1", "//h2", "//h3"]:
        headings = [x.text_content() for x in tree.xpath(h)]
        if headings:
            return headings
    return []


def normalize(s):
    return re.sub(r'\s+', lambda x: '\n' if '\n' in x.group(0) else ' ', s).strip()


def get_text_and_tail(node):
    text = node.text if node.text else ''
    tail = node.tail if node.tail else ''
    return text + ' ' + tail


def get_full_text(tree):
    return normalize('\n'.join([get_text_and_tail(x) for x in tree.iter()]))


def fscore(x, y):
    try:
        z = sum([w in y for w in x]) / len(x)
        z2 = sum([w in x for w in y]) / len(y)
        return (2 * z * z2) / (z + z2)
    except ZeroDivisionError:
        return 0


class lazy_property(object):
    """
    A property that is only computed once per instance and then replaces itself
    with an ordinary attribute. Deleting the attribute resets the property.
    Source: https://github.com/bottlepy/bottle/commit/fa7733e075da0d790d809aa3d2f53071897e6f76
    """  # noqa

    def __init__(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value
