# encoding: utf-8

import logging_helper
from future.utils import iteritems
from configurationutil import (CfgItems,
                               InheritableCfgItem,
                               DefaultInheritableConstant)
from .config import RegisterAPIConfig
from ._constants import ENVIRONMENT_CONFIG, EnvironmentKeysConstant
from .apis import APIS

logging = logging_helper.setup_logging()


class Environment(InheritableCfgItem):
    """ Representation of a single API, overrides InheritableCfgItem. """
    STRICT = False
    DEFAULTS = EnvironmentKeysConstant.apis

    _APIS = None

    def __getitem__(self, item):

        """ Extends InheritableCfgItem.__getitem__ to explode apis param. """

        item_value = super(Environment, self).__getitem__(item)

        if self._APIS is None:
            Environment._APIS = APIS()

        # Attempt to explode API
        if item in self.inheritable_parameters:
            try:
                return self._APIS[item_value]

            except LookupError:
                raise KeyError(u'No \'{api}\' API configuration exists for api family \'{api_type}\', '
                               u'Please check your configuration!'.format(api_type=item,
                                                                          api=item_value))

        return item_value


class Environments(CfgItems):

    """ Environments configuration.

    Get environments object:
    >>> envs = Environments()

    Get A list of available environments:
    >>> list(envs)
    ['production', 'lab']

    Get a specific environment:
    >>> lab_env = envs.lab

    Or:
    >>> lab_env = envs['lab']

    Check whether an environment is used by any APIs:
    >>> bool(lab_env.keys())
    True

    Get a list of API's for an environment:
    >>> lab_env.keys()
    ['family_a', 'family_b']

    """

    def __init__(self):
        """ Initialise the CfgItems class for Environments. """
        super(Environments, self).__init__(cfg_fn=RegisterAPIConfig().environments,
                                           cfg_root=ENVIRONMENT_CONFIG,
                                           key_name=DefaultInheritableConstant.name,
                                           item_class=Environment)

    def get_environments_for_api(self,
                                 api):

        """ Get a list of environments for a specific API.

        :param api:     (string)    API key param for lookup.
        :return:        (list)

        Examples:
        ---------
        Get a list of environments for an API:
        >>> Environments().get_environments_for_api('api_1')
        ['production', 'lab']

        """

        return [k for k, e in iteritems(self) if api in [e[a].key for a in e]]

    def get_environments_for_api_family(self,
                                        family):

        """ Get a list of environments for a specific API.

        :param family:  (string)    API family param for lookup.
        :return:        (list)

        Examples:
        ---------
        Get a list of environments for an API family:
        >>> Environments().get_environments_for_api_family('first_api')
        ['production', 'lab']

        """

        return [k for k, e in iteritems(self) if family in e.keys()]

    def get_host_list(self,
                      environment=None,
                      api=None):

        """ Get a list containing available unique hosts.

        Calling without params will return the full list of unique hosts configured.

        Calling with either environment or api keyword set will limit the list to just
        returning hosts from that environment or api.

        Note however that specifying both environment and api is inefficient as the
        same result can be obtained much quicker using direct access.
        i.e: `Environments()[environment][api].host`.

        :param environment: (string)    Environment name to limit list to.
        :param api:         (string)    API family to limit list to.
        :return:            (list)      List of strings, where the strings are host names.

        Examples (we extract domain only in examples but Host objects are returned):
        ---------
        Get full host list:
        >>> [host.domain for host in Environments().get_host_list()]

        get list of hosts for production environment only:
        >>> [host.domain for host in Environments().get_host_list(environment='production')]

        get list of hosts for example_api API only:
        >>> [host.domain for host in Environments().get_host_list(api='first_api')]

        """

        if environment is not None and api is not None:
            logging.warning(u'If you are specifying both environment and api it '
                            u'is more efficient to use direct access!  '
                            u'i.e: Environments()[environment][api].host')

        hosts = []

        for env in self:
            if environment is None or environment == env:

                for api_name, api_cfg in iteritems(self[env]):
                    if api is None or api == api_name:
                        host = api_cfg.host

                        if host and host not in hosts:
                            hosts.append(host)

        return sorted(hosts, key=lambda x: x.key)

    def get_host_references(self,
                            host=None):

        """ Get a list of Env/API references a particular host is configured for.

        :param host:    (string)    The host to search for references.
        :return:        (list)      List of dicts, where the dicts are of the form:
                                        {
                                            'environment': '<env name (key)>',
                                            'api': '<api family>'
                                        }

        Examples:
        ---------
        Get all references:
        >>> Environments().get_host_references()
        [{'environment': 'production', 'api': 'family_a'}, {'environment': 'production', 'api': 'family_b'}, {'environment': 'lab', 'api': 'family_a'}, {'environment': 'lab', 'api': 'family_b'}]

        Get references for a specific host:
        >>> Environments().get_host_references(u'p2.example.com')
        [{'environment': 'production', 'api': 'family_b'}]

        Get list of unique apis from references:
        >>> list({ref[u'api'] for ref in Environments().get_host_references()})
        ['family_a', 'family_b']

        """

        references = []

        for _, env in iteritems(self):
            for api_key, api in iteritems(env):
                reference = dict(environment=env.key,
                                 api=api_key)

                if (api.host.domain == host or host is None) and reference not in references:
                    references.append(reference)

        return references

    def get_environments_for_location(self,
                                      location):

        """ Get a list of environments for a location.

        :param location:    (string)    The location to search for.
        :return:            (list)      List of environment names.

        Examples:
        ---------
        Get all environments for location:
        >>> Environments().get_environments_for_location(u'somewhere')
        ['production']

        """

        environments = []

        for env_name, env in iteritems(self):
            if env.location == location:
                environments.append(env_name)

        return environments
