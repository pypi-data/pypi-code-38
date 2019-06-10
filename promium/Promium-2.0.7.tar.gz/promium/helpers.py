
from six.moves.urllib.parse import urlparse


class ParseUrl(object):

    def __init__(self, url):
        self.url = url

    def __repr__(self):
        return self.url

    @property
    def scheme(self):
        """
        :return: scheme, for example: http or https
        """
        parse_url = urlparse(self.url)
        return parse_url.scheme

    @property
    def hostname(self):
        """
        :return: hostname, for example: prom.ua
        """
        parse_url = urlparse(self.url)
        return parse_url.netloc.split(':')[0]

    @property
    def port(self):
        """
        :return: port
        """
        parse_url = urlparse(self.url)
        parse_netloc_split = parse_url.netloc.split(u':')
        if len(parse_netloc_split) > 1:
            return parse_netloc_split[-1]

    @property
    def path(self):
        """
        :return: hierarchical path, for example: /Zhenskii-platya
        """
        parse_url = urlparse(self.url)
        if parse_url.path:
            return parse_url.path

    @property
    def params(self):
        """
        :return: parameters for last path element
        """
        parse_url = urlparse(self.url)
        if parse_url.params:
            return parse_url.params

    @property
    def query(self):
        """
        :return: query component
        """
        parse_url = urlparse(self.url)
        if parse_url.query:
            return dict(
                [query.split(u'=') for query in parse_url.query.split(u'&')]
            )

    @property
    def fragment(self):
        """
        :return: fragment identifier (#)
        """
        parse_url = urlparse(self.url)
        if parse_url.fragment:
            return parse_url.fragment
