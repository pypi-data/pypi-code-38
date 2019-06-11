# encoding: utf-8

import logging_helper
from configurationutil import (CfgItems,
                               InheritableCfgItem, 
                               DefaultInheritableConstant)
from .config import RegisterAPIConfig
from ._constants import (HOST_CONFIG,
                         HostKeysConstant)

logging = logging_helper.setup_logging()


class Host(InheritableCfgItem):
    """ Representation of a single Host, overrides InheritableCfgItem. """
    STRICT = False
    DEFAULT_PARAMS = {
        HostKeysConstant.protocol: u'http',
        HostKeysConstant.domain: u'',
        HostKeysConstant.port: 80,
        HostKeysConstant.secret_key: u'',
        HostKeysConstant.user: u'',
        HostKeysConstant.password: u''
    }

    @property
    def url(self):
        """ Construct the full url for this host. """
        url = u'{domain}:{port}'.format(domain=self.domain,
                                        port=self.port)

        if self.protocol:
            url = u'{proto}://{url}'.format(proto=self.protocol,
                                            url=url)

        return url


class Hosts(CfgItems):

    """ Host configuration.

    Get hosts object:
    >>> hosts = Hosts()

    Get A list of available Hosts:
    >>> hosts.keys
    ['prod_1', 'prod_2', 'lab_1']

    """

    def __init__(self):
        super(Hosts, self).__init__(cfg_fn=RegisterAPIConfig().hosts,
                                    cfg_root=HOST_CONFIG,
                                    key_name=DefaultInheritableConstant.name,
                                    item_class=Host)

    def convert_domain_to_friendly_name(self,
                                        domain):

        """ Converts a domain to it's registered name (Host.key).

        :param domain:  (string)    Domain name.
        :return:        (string)    key for the matching Host object.
        """

        # Attempt to lookup friendly name
        for host in self:
            if self[host].domain == domain:
                return host

        logging.debug(u'No friendly name available for domain: {domain}'.format(domain=domain))
        return None

    def convert_friendly_name_to_host(self,
                                      name):

        """ Converts a friendly name (Host.key) into its Host object.

        This is the same as Hosts()[name] however it returns None if nothing
        found rather than raising a KeyError.

        :param name:    (string)    The key name
        :return:        (Host)
        """

        try:
            return self[name]

        except KeyError:
            logging.debug(u'No domain available for name: {name}'.format(name=name))
            return None
