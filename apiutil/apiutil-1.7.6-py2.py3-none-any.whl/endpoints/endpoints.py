# encoding: utf-8

from difflib import SequenceMatcher
from configurationutil import (CfgItems, 
                               InheritableCfgItem, 
                               DefaultInheritableConstant)
from .config import RegisterAPIConfig
from ._constants import (ENDPOINT_CONFIG,
                         EndpointKeysConstant)


class Endpoint(InheritableCfgItem):
    """ Representation of a single Endpoint, overrides InheritableCfgItem. """
    STRICT = False
    DEFAULT_PARAMS = {
        EndpointKeysConstant.path: u'/',
        EndpointKeysConstant.params: None
    }

    @property
    def url(self):
        """ Construct the full url for this endpoint. """
        return u'{host_url}{path}'.format(host_url=self.host.url,
                                          path=self.path)

    def match_url(self,
                  url):

        """ Work out whether the url captured is from this endpoint.

        :param url:     (string)    Full URL to determine the match for.
        :return:        (int)        -1: No match found.
                                      0: Host match only, not specifically a match to this endpoint.
                                    > 0: Path match of x characters from start of path.
        """

        url_match_length = -1

        if u'://' in url:
            protocol, url = url.split(u'://')

        hostname, path = url.split(u'/', 1)

        if self.host:
            if u':' in hostname:
                hostname, port = hostname.split(u':')

                if int(port) != self.host.port:
                    return url_match_length

            if hostname != self.host.domain:
                return url_match_length

            url_match_length = 0  # Match for hostname

        # Only attempt a path match if one of the following conditions is met:
        #   --> we don't have a host. (host agnostic endpoint)
        #   --> We have a host and it has matched.
        if not self.host or url_match_length >= 0:
            path_match_length = self.match_path(path=u'/{path}'.format(path=path))  # Re-attach path root '/'

            if path_match_length > 0:
                url_match_length = path_match_length

        return url_match_length

    def match_path(self,
                   path):

        """ Work out whether the path captured is from this endpoint.

        :param path:    (string)    Full Path to determine the match for.
        :return:        (int)         0: No match found.
                                    > 0: Path match of x characters from start of path.
        """

        # See how much of the path we can match
        matcher = SequenceMatcher(a=self.path,
                                  b=path)
        match = matcher.find_longest_match(0, len(self.path),
                                           0, len(path))

        # Ensure any match is at the start of the string
        return match[2] if match[0] == match[1] == 0 else 0


class Endpoints(CfgItems):

    """ Endpoint configuration.

    Get endpoints object:
    >>> endpoints = Endpoints()

    Get A list of available Endpoints:
    >>> endpoints.keys
    ['ep_1', 'ep_2', 'ep_3', 'ep_4']

    """

    def __init__(self,
                 allowed_endpoints=None,
                 host=None):

        super(Endpoints, self).__init__(cfg_fn=RegisterAPIConfig().endpoints,
                                        cfg_root=ENDPOINT_CONFIG,
                                        key_name=DefaultInheritableConstant.name,
                                        allowed_items=allowed_endpoints,
                                        item_class=Endpoint,
                                        host=host)
