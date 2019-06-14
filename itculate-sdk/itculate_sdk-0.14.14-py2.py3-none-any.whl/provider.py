#
# (C) ITculate, Inc. 2015-2017
# All rights reserved
# Licensed under MIT License (see LICENSE)
#

import json
import logging
import binascii
import pprint

import six
from .local_credentials import read_local_credentials
from . import __version__

_DEFAULT_API_URL = "https://api.itculate.io/api/v1"
_DEFAULT_AGENT_REST_URL = "http://localhost:8000"

logger = logging.getLogger(__name__)


class ProviderRegister(type):
    """
    Meta class for Provider - to auto register implementations
    """
    registry = {}

    def __new__(mcs, name, bases, attrs):
        new_cls = type.__new__(mcs, name, bases, attrs)

        if name != "Provider":
            mcs.registry[name] = new_cls

        return new_cls


class Provider(object):
    __metaclass__ = ProviderRegister

    def __init__(self, settings):
        self.settings = settings
        self.host = settings.get("host")

        self._name_to_payload_generator = {}

    @classmethod
    def factory(cls, settings):
        provider_class_name = settings.get("provider", "SynchronousApiUploader")
        assert provider_class_name in ProviderRegister.registry, \
            "provider can be one of {}".format(ProviderRegister.registry.keys())

        provider_class = ProviderRegister.registry[provider_class_name]
        return provider_class(settings)

    def handle_payload(self, payload):
        raise NotImplementedError()

    def flush_now(self, payload_generators):
        """
        Sends all unsent data without waiting

        :param: collections.Iterable[PayloadProvider]: iterable to allow us to get all payloads to flush
        :return: number of payloads flushed
        """
        count = 0

        for payload_generator in six.itervalues(payload_generators):
            payload = payload_generator.flush()
            if payload is not None:
                self.handle_payload(payload)
                count += 1

        return count


class AgentForwarder(Provider):
    """
    Forward payloads over HTTP to the ITculate agent.

    This is typically used to forward topology, and dictionary.

    Time series samples are typically forwarded using the 'statsd' protocol (via UDP) and the agent will use
    mappings to convert these samples to ITculate time series sample objects.

    Expected settings:
        provider:               "AgentForwarder"
        host:                   (will default to hostname)
        server_url:             (defaults to 'http://127.0.0.1:8000/upload')
    """

    def __init__(self, settings):
        super(AgentForwarder, self).__init__(settings)
        self.server_url = settings.get("server_url", _DEFAULT_AGENT_REST_URL)

        import requests
        self.session = requests.session()
        self.session.verify = True
        self.session.headers["Content-Type"] = "application/json"
        self.session.headers["Accept"] = "application/json"

    def handle_payload(self, payload):
        """
        Sends (over TCP) the payload to the agent. This is supposed to end as quickly as possible and take as little
        overhead as possible from the client side

        :type payload: dict
        """

        payload["collector_version"] = __version__
        payload["host"] = self.host

        # Use the 'agent_api' attribute to figure out where to route this payload
        r = self.session.post("{}/upload".format(self.server_url),
                              data=json.dumps(payload),
                              headers={"Content-Type": "application/json"})
        r.raise_for_status()

        return r.json()


class SynchronousApiUploader(Provider):
    """
    Upload a payload to an ITculate REST API server.
    This is used to upload immediately the payload. For better performance, use the ITculate agent instead.

    Expected settings:
        provider:               "SynchronousApiUploader"
        host:                   (will default to hostname)
        server_url:             (will default to public REST API)
        https_proxy_url         (if applicable URL (including credentials) for HTTPS proxy)
        api_key:                (will try to use local credentials if not provided)
        api_secret:             (will try to use local credentials if not provided)
        role:                   (role to look in local credentials)
        home_dir:               (override location of user home dir)
    """

    def __init__(self, settings):
        super(SynchronousApiUploader, self).__init__(settings)

        self.api_key = self.settings.get("api_key")
        self.api_secret = self.settings.get("api_secret")
        self.server_url = self.settings.get("server_url", _DEFAULT_API_URL)
        self.https_proxy_url = self.settings.get("https_proxy_url")

        if self.api_key is None or self.api_secret is None:
            # Read permissions from local file (under ~/.itculate/credentials)
            self.api_key, self.api_secret = read_local_credentials(role=self.settings.get("role", "upload"),
                                                                   home_dir=self.settings.get("home_dir"))

        assert self.api_key and self.api_secret, \
            "API key/secret have to be provided (either in config or in local credentials file)"

    def handle_payload(self, payload):
        """
        Upload a payload to ITculate API

        :param dict payload: payload to upload
        """

        # Only now import the requirements for sending data to the cloud
        import msgpack
        import zlib
        from .connection import ApiConnection
        connection = ApiConnection(api_key=self.api_key,
                                   api_secret=self.api_secret,
                                   server_url=self.server_url,
                                   https_proxy_url=self.https_proxy_url)

        data_to_upload = {
            "tenant_id": payload["tenant_id"],
            "collector_id": payload["collector_id"],
            "collector_version": __version__,
            "host": self.host,
            "compressed_payload": binascii.hexlify(zlib.compress(msgpack.dumps(payload))),
        }

        return connection.post("upload", json_obj=data_to_upload)


class InMemory(Provider):
    """
    Used by the agent as a buffer to hold accumulated data in-memory before sending it.

    Expected settings:
        provider: "StoreInMemory"
    """

    def __init__(self, settings):
        super(InMemory, self).__init__(settings)
        self._payloads = {}  # type: dict[tuple, dict]

    def handle_payload(self, payload):
        """
        Sends (over TCP) the payload to the agent. This is supposed to end as quickly as possible and take as little
        overhead as possible from the client side

        :type payload: dict
        """

        payload_key = (payload["tenant_id"], payload["collector_id"])
        self._payloads[payload_key] = payload

    def pop(self):
        """
        Gets (and removes) the data stored in memory (called by the agent when it is time to upload data)

        :rtype: list[dict]
        """

        local_payloads, self._payloads = (self._payloads, {})
        return local_payloads.values()


class Print(Provider):
    """
    Used by the agent as a buffer to hold accumulated data in-memory before sending it.

    Expected settings:
        provider: "StoreInMemory"
    """

    def __init__(self, settings):
        super(Print, self).__init__(settings)

    def handle_payload(self, payload):
        """
        Sends (over TCP) the payload to the agent. This is supposed to end as quickly as possible and take as little
        overhead as possible from the client side

        :type payload: dict
        """

        pprint.pprint(dict(payload))
        # payload_key = (payload["tenant_id"], payload["collector_id"])
