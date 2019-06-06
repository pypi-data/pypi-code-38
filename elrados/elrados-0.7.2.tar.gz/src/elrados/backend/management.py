"""Server Management tools."""
# pylint: disable=invalid-name,too-many-ancestors
# pylint: disable=superfluous-parens,no-member,protected-access
import json

from django.contrib import admin
from autobahn.twisted.websocket import (WebSocketServerProtocol,
                                        WebSocketServerFactory)

from elrados.backend.cache import Cache


class BroadcastServerProtocol(WebSocketServerProtocol):
    """"Protocol for a Websocket server which broadcasts messages to clients"""
    def onOpen(self):
        """"Register the client for future broadcasts."""
        super(BroadcastServerProtocol, self).onOpen()
        self.factory.register(self)

    def connectionLost(self, reason):
        """"Unregister the client from future broadcasts."""
        super(BroadcastServerProtocol, self).connectionLost(reason)
        self.factory.unregister(self)


class BroadcastServerFactory(WebSocketServerFactory):
    """Broadcast server factory of the websocket."""
    protocol = BroadcastServerProtocol

    def __init__(self, url, settings=None):
        super(BroadcastServerFactory, self).__init__(url=url)
        self.clients = set()
        self.cache = Cache(self)
        self.settings = settings if settings is not None else {}

    def initialize_resources(self, resources):
        """Initialize cache resources."""
        display_attrs = {
            resource.__name__: admin.site._registry[resource].list_display
            for resource in resources
            }
        self.cache.initialize_display_list_cache(display_attrs)
        self.cache.initialize_resources_cache(resources)

        # send to all users the extracted resources
        self.cache.update_users_display_list()
        self.cache.update_users_resources_cache()
        print("[Frontend] Initialize done!")

    def broadcast(self, message, isBinary):
        """Broadcast a message to the clients."""
        for client in self.clients:
            client.sendMessage(message, isBinary=isBinary)

    def register(self, client):
        """Register new user to the websocket and initialize its data."""
        self.clients.add(client)
        client.sendMessage(json.dumps(
            {
                "event_type": "initialize-settings",
                "content": self.settings
                }
            ), False)
        client.sendMessage(json.dumps(
            {
                "event_type": "initialize-display-list",
                "content": self.cache.display_list_cache
                }
            ), False)
        client.sendMessage(json.dumps(
            {
                "event_type": "initialize-cache",
                "content": self.cache.resources_cache
                }
            ), False)

    def unregister(self, client):
        """Unregister user from the websocket."""
        self.clients.remove(client)
