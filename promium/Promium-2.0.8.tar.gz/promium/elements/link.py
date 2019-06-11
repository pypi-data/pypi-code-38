
import requests

from promium.base import Element
from promium.helpers import ParseUrl


class Link(Element):

    @property
    def href(self):
        return self.get_attribute("href")

    @property
    def parse_url(self):
        """
        Using parse_url to parse href. Can get attributes:
        - scheme
        - host
        - sub_domain
        - port
        - path
        - params
        - query
        - fragment
        - product_id
        """
        return ParseUrl(self.href)

    @property
    def response(self):
        return requests.get(self.href, verify=False, timeout=10)

    @property
    def get_status_code(self):
        """Gets status requests code from link"""
        return self.response.status_code
