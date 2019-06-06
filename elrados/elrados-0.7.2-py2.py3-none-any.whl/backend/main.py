"""Elrados web-socket server starter."""
# pylint: disable=superfluous-parens
# pylint: disable=no-member
# pylint: disable=protected-access
# pylint: disable=invalid-name
import os

import crochet
import yaml
from attrdict import AttrDict
from twisted.internet import reactor
from django.db.models.signals import post_save
from django.contrib.auth.models import User, Group
from rotest.management import ResourceData
from rotest.common.config import search_config_file
from rotest.management.utils.resources_discoverer import get_resources

from elrados.backend.management import BroadcastServerFactory

SERVER_PORT = 9000


class WebsocketService(object):
    """Websocket service that is exposed to the user of elrados."""
    def __init__(self, settings=None):
        print("[Frontend] initializing websocket service")
        self.factory = BroadcastServerFactory(
            u'ws://0.0.0.0:{}'.format(SERVER_PORT), settings)

    @crochet.run_in_reactor
    def create_server(self, init_list):
        """Create new user and listen to the server port."""
        self.factory.initialize_resources(init_list)
        reactor.listenTCP(SERVER_PORT, self.factory)

    def send_to_client(self, sender, instance, **kwargs):
        """Send update message to client."""
        self.factory.cache.update_resource(sender, instance, **kwargs)


def read_config():
    """Read from rotest.yml config elrados segment."""
    config_path = search_config_file()
    if config_path is not None:
        with open(config_path, "r") as config_file:
            configuration_content = config_file.read()

        yaml_configuration = yaml.load(configuration_content)

    else:
        yaml_configuration = {}

    return AttrDict(yaml_configuration.get("elrados", {}))


def setup_server():
    """Start the websocket server."""
    crochet.setup()

    config = read_config()

    resource_models = [User, Group]
    resource_models.extend(
        resource.DATA_CLASS
        for resource in get_resources().values()
        if resource.DATA_CLASS not in (None, NotImplemented)
        and issubclass(resource.DATA_CLASS, ResourceData))

    default_resource = config.get("default_resource", None)
    if default_resource is None:
        default_resource = resource_models[-1].__name__

    if os.environ.get("RUN_MAIN") == "true":
        backend = WebsocketService(settings={
            "default_resource": default_resource
        })
        backend.create_server(resource_models)
        post_save.connect(backend.send_to_client,
                          sender='management.ResourceData',
                          weak=False)

        for resource_data in resource_models:
            post_save.connect(backend.send_to_client,
                              sender=resource_data,
                              weak=False)
