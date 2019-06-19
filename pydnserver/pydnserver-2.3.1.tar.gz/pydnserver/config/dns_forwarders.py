# encoding: utf-8

import logging_helper
from configurationutil import Configuration, cfg_params
from ipaddress import IPv4Network, IPv4Address
from .._metadata import __version__, __authorshort__, __module_name__
from .._exceptions import NoForwardersConfigured, MultipleForwardersForInterface
from ..resources import templates, schema

logging = logging_helper.setup_logging()

# Register Config details (These are expected to be overwritten by an importing app)
cfg_params.APP_NAME = __module_name__
cfg_params.APP_AUTHOR = __authorshort__
cfg_params.APP_VERSION = __version__

# Set the config initialisation parameters
DNS_SERVERS_CFG = u'dns_forwarders'
TEMPLATE = templates.dns_forwarders

DEFAULT_FORWARDER = u'0.0.0.0'


def get_all_forwarders(interface=None):

    # Retrieve configuration instance
    cfg = Configuration()

    # Register configuration
    cfg.register(config=DNS_SERVERS_CFG,
                 config_type=cfg_params.CONST.json,
                 template=TEMPLATE,
                 schema=schema.dns_forwarders)

    if interface is not None:
        key = u'{c}.{n}'.format(c=DNS_SERVERS_CFG,
                                n=interface)

        try:
            dns_forwarders = cfg[key]

        except KeyError as err:
            raise NoForwardersConfigured(err)

        else:
            if len(dns_forwarders) == 0:
                raise NoForwardersConfigured(u'No Forwarders have been configured for {int}'.format(int=interface))

    else:
        dns_forwarders = cfg[DNS_SERVERS_CFG]

        if interface is not None:
            # Only pass the forwarders that match the interface! (should only be one)
            dns_forwarders = [forwarder
                              for forwarder in dns_forwarders
                              if IPv4Address(interface) in IPv4Network(forwarder)]

            if len(dns_forwarders) > 1:
                raise MultipleForwardersForInterface(u'There should only be one configuration per interface, '
                                                     u'not counting the default forwarder!')

    logging.debug(dns_forwarders)

    # Return a copy so that modifications of the retrieved do not get modified in config unless explicitly requested!
    return dns_forwarders[:] if type(dns_forwarders) == list else dns_forwarders.copy()


def get_forwarders_by_interface(interface):
    return get_all_forwarders(interface=interface)


def get_default_forwarder():
    return get_all_forwarders(interface=DEFAULT_FORWARDER)
