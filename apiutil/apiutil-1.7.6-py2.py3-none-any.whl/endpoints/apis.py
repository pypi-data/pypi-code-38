# encoding: utf-8

from future.utils import iteritems
from configurationutil import (CfgItems,
                               InheritableCfgItem,
                               DefaultInheritableConstant)
from classutils.decorators import class_cache_result, clear_class_cached_results
from .config import RegisterAPIConfig
from ._constants import API_CONFIG, APIKeysConstant
from .hosts import Hosts
from .endpoints import Endpoints


class API(InheritableCfgItem):
    """ Representation of a single API, overrides InheritableCfgItem. """
    STRICT = False
    DEFAULT_PARAMS = {
        APIKeysConstant.host: u'',
        APIKeysConstant.endpoints: [u'default_root'],
        APIKeysConstant.params: None
    }

    _HOSTS = None

    @clear_class_cached_results
    def invalidate(self):
        """ Call to invalidate API memory caches """
        pass

    def __getitem__(self, item):

        """ Extends InheritableCfgItem.__getitem__ to explode default params.

        Will get the API configuration as InheritableCfgItem.__getitem__ but will update
        the following:
            --> host:       Validate host config exists and retrieve the Host object from self.HOSTS.
            --> endpoints:  For each listed endpoint, validate endpoint config exists and retrieve
                            the Endpoint object from self.ENDPOINTS.
        Note: if host or any endpoints are invalid a KeyError will be raised.

        """

        item_value = super(API, self).__getitem__(item)

        if self._HOSTS is None:
            API._HOSTS = Hosts()

        # Attempt to explode Host
        if item == APIKeysConstant.host:
            try:
                return self._HOSTS[item_value]

            except LookupError:
                raise KeyError(u'No Host configuration exists for {host}! '
                               u'Please check your configuration!'.format(host=item_value))

        # Attempt to explode Endpoints
        if item == APIKeysConstant.endpoints:
            return self._get_endpoints_obj(allowed_endpoints=item_value,
                                           host=self.host)

        return item_value

    @class_cache_result
    def _get_endpoints_obj(self,
                           **params):
        return Endpoints(**params)

    def match_url(self,
                  url):

        """ Work out whether the url captured is from this endpoint.

        :param url:     (string)    Full URL to determine the matches for.
        :return:        (list)      List of matched endpoints for the url.
                                    Each item in the list is a tuple of the form:
                                        (API Family, API Name, Endpoint Name)
        """

        best_match = -1
        matched_endpoints = []

        for endpoint_name, endpoint in iter(self.endpoints.items()):
            matched_len = endpoint.match_url(url)

            if matched_len > -1:
                match_ref = (self.family, self.key, endpoint_name)

                if matched_len > best_match:
                    # Better than our best match so restart the list
                    matched_endpoints = [match_ref]
                    best_match = matched_len

                elif matched_len == best_match and match_ref not in matched_endpoints:
                    # Same as best match to append to list
                    matched_endpoints.append(match_ref)

        return matched_endpoints, best_match


class APIS(CfgItems):

    """ API configuration.

    Get environments object:
    >>> apis = APIS()

    Get A list of available APIs:
    >>> list(apis)
    ['example_api', 'example_api_2']

    """

    def __init__(self):
        super(APIS, self).__init__(cfg_fn=RegisterAPIConfig().apis,
                                   cfg_root=API_CONFIG,
                                   key_name=DefaultInheritableConstant.name,
                                   item_class=API)

    @clear_class_cached_results
    def invalidate(self):
        """ Call to invalidate APIS memory caches """
        for api in self:
            self[api].invalidate()

    def get_api_family(self,
                       family=None):

        """ Get and return a list of APIs belonging to an API family.

        :param family:  (string) The API family to get a list of APIs for.
                        default=None (the default family)
        :return:        (list)   List of API names for this family.
        """

        return [api_name for api_name, api in iteritems(self) if api.family == family]

    @class_cache_result
    def get_endpoint_for_request(self,
                                 url):

        """ Determine and return the API / Endpoint config for a URL.

        :param url:     (string)    Full URL to determine the config for.
        :return:        (tuple)     Match tuple values: (API Family, API Name, Endpoint Name)

        Examples:
        ---------
        Work out the Env / API configuration for a request:
        >>> APIS().get_endpoint_for_request(u'http://api.example.com/1.1/sometest')
        'example_api'

        """

        best_match = -1
        matched_endpoints = []

        for api in self.values():
            matches, match_length = api.match_url(url)

            if matches:
                if match_length > best_match:
                    matched_endpoints = matches
                    best_match = match_length

                elif match_length == best_match:
                    matched_endpoints += matches

        if len(matched_endpoints) == 1:
            return matched_endpoints.pop()

        if len(matched_endpoints) == 0:
            raise LookupError(u'No Endpoint match for: {url}'.format(url=url))

        host_names = set(ep[1] for ep in matched_endpoints)
        hosts = ["{host_name} ({endpoints})"
                 .format(host_name=host_name,
                         endpoints=", ".join([ep[-1]
                                              for ep in matched_endpoints
                                              if ep[1] == host_name]))
                 for host_name in host_names]

        raise LookupError(u'Check your config...\n'
                          u'    Multiple matching Endpoints for: {url}\n'
                          u'    This may mean the specific endpoint for this request is not defined.\n'
                          u'    Matched host: {hosts}\n'
                          .format(hosts='\n    Matched host: '.join(hosts),
                                  url=url))
