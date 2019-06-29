import hashlib
import websocket
import time
import json
import requests
import urllib
import logging
from pyhomee.util import get_token
from pyhomee.models import Node, Group, Homeegram, Relationship
from pyhomee.subscribe import SubscriptionRegistry

_LOGGER = logging.getLogger(__name__)


class HomeeCube():

    def __init__(self, hostname, username, password):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.token = self._get_token()
        self.nodes = []
        self.groups = []
        self.relationships = []
        self.homeegrams = []

        self._get_all()
        self.registry = SubscriptionRegistry(self)
        self.registry.start()

    def _get_token(self):
        url = "http://{}:7681/access_token".format(self.hostname)
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        form = {
            "device_name": "Home Assistant 2",
            "device_hardware_id": "homeassistant",
            "device_os": 5,
            "device_type": 3,
            "device_app": 1
        }
        auth = (self.username, hashlib.sha512(self.password.encode('utf-8')).hexdigest())
        r = requests.post(url, auth=auth, data=form, headers=headers)
        try:
            token = r.text.split("&")[0].split("=")[1]
        except:
            raise Exception("Authenticationfailed")
        return token

    def get_token(self):
        return self.token

    def _get_all(self):
        ws = websocket.create_connection("ws://{}:7681/connection?access_token={}".format(self.hostname, self.token),
                                         subprotocols=["v2"])
        ws.send("GET:all")
        nodes = ws.recv()
        ws.close()
        try:
            parsed = json.loads(nodes)
        except:
            return
        self.all_config = parsed["all"]
        self._get_nodes()
        self._get_groups()
        self._get_relationships()
        self._get_homeegrams()

    def _get_nodes(self):
        if "nodes" in self.all_config:
            for node in self.all_config["nodes"]:
                self.nodes.append(Node(node))
        return

    def _get_groups(self):
        if "groups" in self.all_config:
            for group in self.all_config["groups"]:
                self.groups.append(Group(group))
        return

    def _get_relationships(self):
        if "relationships" in self.all_config:
            for relationship in self.all_config["relationships"]:
                self.relationships.append(Relationship(relationship))
        return

    def _get_homeegrams(self):
        if "homeegrams" in self.all_config:
            for homeegram in self.all_config["homeegrams"]:
                self.homeegrams.append(Homeegram(homeegram))
        return

    def get_nodes(self):
        return self.nodes

    def get_groups(self):
        return self.groups

    def get_relationships(self):
        return self.relationships

    def get_homeegrams(self):
        return self.homeegrams

    def get_group_by_name(self, name):
        for group in self.groups:
            if group.name == name:
                return group
        return None

    def get_group_node_ids(self, group_id):
        nodes = []
        for rel in self.relationships:
            if rel.group_id == group_id and rel.node_id != 0:
                nodes.append(rel.node_id)
        return nodes

    def register(self, node, callback):
        self.registry.register(node, callback)

    def send_node_command(self, node, attribute, target_value):
        self.registry.send_node_command(node, attribute, target_value)

    def play_homeegram(self, id):
        self.registry.play_homeegram(id)

    def stop(self):
        self.registry.stop()
