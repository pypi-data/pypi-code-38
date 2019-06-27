from __future__ import absolute_import

import logging
import re
from threading import RLock

import sentry_sdk
import zmq
from om.message import Message, Topic
from sentry_sdk.transport import Transport

dsn_regex = re.compile(r'([a-z0-9]+):\/\/([a-z0-9:]+)@([a-z0-9\.]+)\/(\d+)')


class ZeroMQTransport(Transport):
    def __init__(self, config, options=None):
        super(ZeroMQTransport, self).__init__(options)
        context = zmq.Context()
        self.pub = context.socket(zmq.PUB)
        self.pub.connect("tcp://{}:{}".format(config.BROKER_HOST, config.BROKER_SUB_PORT))
        self.name = config.NAME
        self.lock = RLock()

    def capture_event(self, event):
        message = Message(name=self.name, type="sentry")
        message.update(event=event)
        with self.lock:
            message.to_socket(self.pub, Topic.SENTRY)

    def flush(self, timeout, callback=None):
        pass

    def kill(self):
        pass


def sentry_init(config, extras=None, **kwargs):
    """
    This function initializes Sentry with our predefined values. This function also check if Sentry should be
    initialized.

    :param config: current config
    :param extras: global extras that should be added to message
    :param kwargs: client supported **kwargs see ClientOptions
    """
    if activate_sentry(config):
        if not extras:
            extras = {}
        extras.update(_extra_from_config(config))

        transport = ZeroMQTransport(config)
        environment = environment_from_config(config)
        sentry_sdk.init(
            None, release=config.VERSION, server_name=config.RESOURCE, environment=environment, transport=transport,
            **kwargs
        )
        with sentry_sdk.configure_scope() as scope:
            for key, value in extras.items():
                scope.set_extra(key, value)


def activate_sentry(config):
    """
    This function checks if for the given config Sentry should be activated or not.

    :param config: current configuration
    :return: bool
    """
    if config.VERSION == "unknown":
        logging.info("not activating sentry because version is unknown")
        return False
    return True


def parse_dsn(dsn):
    """
    This function parses a given DSN into it's components.

    :param dsn: The DSN from sentry
    :return: dictionary with values if DSN could be matched against the regex, if the given DSN is deprecated then the
    secret is in the 'public_key' field
    """
    if dsn:
        matches = dsn_regex.search(dsn)
        if matches:
            return {
                "protocol": matches.group(1),
                "public_key": matches.group(2),
                "host": matches.group(3),
                "project_id": matches.group(4),
            }
    return {}


def environment_from_config(config):
    """
    This functions returns either the environment of the current configuration.

    :param config: current configuration
    :return: 'staging' or 'production'
    """
    if hasattr(config, "DEVICE_HOST") and ("test" in config.DEVICE_HOST):
        return "staging"
    else:
        return "production"


def _extra_from_config(config):
    extra = {
        "name": config.NAME,
    }
    if hasattr(config, "GATE"):
        extra["gate"] = config.GATE
    return extra
