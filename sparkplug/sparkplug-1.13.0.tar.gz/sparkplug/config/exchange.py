"""Exchange configuration
=========================

.. highlight:: cfg

Sparkplug can automatically declare and configure exchanges on startup::

    [exchange:postoffice]
    # The exchange type ('direct', 'fanout', or 'topic')
    type = direct
    # Will the exchange be declared as durable, and survive broker restarts?
    durable = True
    # Will the exchange be declared as auto-deleted, and be removed if all
    # producers exit?
    auto_delete = False

If you only need to check if an exchange exists, rather than creating one,
it's sufficient to declare it passive::

    [exchange:expected]
    passive = True
    type = direct

This is handy if a consumer needs a particular exchange in order to publish
responses.

Any exchanges used in binding_ configurations must be declared in
sparkplug's configuration file.

.. _binding: `Binding configuration`_
"""

from sparkplug.config import DependencyConfigurer
from sparkplug.config.types import convert, parse_bool
from sparkplug.logutils import LazyLogger

_log = LazyLogger(__name__)


class ExchangeConfigurer(DependencyConfigurer):
    def __init__(self, name, type, **kwargs):
        DependencyConfigurer.__init__(self)
        
        self.exchange = name
        self.type = type
        
        create_args = dict(kwargs)
        convert(create_args, 'durable', parse_bool)
        convert(create_args, 'auto_delete', parse_bool)
        convert(create_args, 'internal', parse_bool)
        convert(create_args, 'passive', parse_bool)
        self.create_args = create_args
    
    def start(self, channel):
        _log.debug("Declaring %s exchange %s (%r)", self.type, self.exchange, self.create_args)
        
        channel.exchange_declare(
            exchange=self.exchange,
            type=self.type,
            **self.create_args
        )

    def __repr__(self):
        return "Exchange(name={0.exchange}, type={0.type})".format(self)
