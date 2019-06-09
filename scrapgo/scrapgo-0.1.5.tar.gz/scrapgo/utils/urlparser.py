import os
from urllib.parse import urlparse, urlunparse, parse_qsl, parse_qs, urljoin


def abs_path(root, url):
    # print('abs_path:root', root)
    # print('abs_path:url', url)
    return urljoin(root, url)


def parse_path(url):
    p = urlparse(url)
    args = '', '', p.path, p.params, p.query, p.fragment
    return urlunparse(args)


def parse_root(url):
    p = urlparse(url)
    args = p.scheme, p.netloc, '', '', '', ''
    return urlunparse(args)


def parse_query(url, qsl=True):
    parse = urlparse(url)
    queryset = parse_qsl(parse.query) if qsl is True else parse_qs(parse.query)
    return dict(queryset)


def parse_src(url):
    p = urlparse(url)
    return os.path.basename(p.path)


def queryjoin(url, params=None):
    r = Request('GET', url, params=params)
    s = Session()
    url = s.prepare_request(r).url
    s.close()
    return url


def queryjoin(url, query=None):
    if query is None:
        return url
    qsl = ['{}={}'.format(qry, val) for qry, val in query.items()]
    qs = '&'.join(qsl)
    p = urlparse(url)
    args = p.scheme, p.netloc, p.path, p.params, qs, p.fragment
    return urlunparse(args)


def filter_params(url, fields):
    if fields is None:
        return url
    p = urlparse(url)
    query = parse_query(url)
    qsl = ['{}={}'.format(q, query.get(q, '')) for q in fields]
    qs = '&'.join(qsl)
    p = urlparse(url)
    args = p.scheme, p.netloc, p.path, p.params, qs, p.fragment
    return urlunparse(args)
