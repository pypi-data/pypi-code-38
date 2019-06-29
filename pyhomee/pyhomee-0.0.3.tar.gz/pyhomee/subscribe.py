"""Module to listen for homee events."""
import collections
import json
import logging
import sched
import threading
import time

import websocket

from pyhomee.models import Attribute, Node, Group

_LOGGER = logging.getLogger(__name__)


class SubscriptionRegistry(object):
    """Class for subscribing to homee events."""

    def __init__(self, cube):
        """Setup websocket."""
        self.cube = cube
        self.hostname = cube.hostname
        self.connected = False
        self._nodes = {}
        self._groups = []
        self._callbacks = collections.defaultdict(list)
        self._exiting = False
        self._event_loop_thread = None
        self.ping_scheduler = sched.scheduler(time.time, time.sleep)

    def register(self, node, callback):
        """Register a callback.

        node: node to be updated by subscription
        callback: callback for notification of changes
        """
        if not node:
            _LOGGER.error("Received an invalid node: %r", node)
            return

        _LOGGER.debug("Subscribing to events for %s", node)
        self._callbacks[node.id].append(callback)

    def join(self):
        """Don't allow the main thread to terminate until we have."""
        self._event_loop_thread.join()

    def start(self):
        """Start a thread to connect to homee websocket."""
        self._event_loop_thread = threading.Thread(target=self._run_event_loop,
                                                   name='Homee Event Loop Thread')
        self._event_loop_thread.deamon = True
        self._event_loop_thread.start()
        _LOGGER.info("Thread started")

    def stop(self):
        """Tell the event loop thread to terminate."""
        try:
            self.ws.close()
        except:
            pass
        try:
            self.ping_scheduler.cancel(self.ping_event)
        except:
            pass
        self.join()
        _LOGGER.info("Terminated thread")

    def restart(self):
        _LOGGER.info("Restarting homee websocket")
        try:
            self.stop()
        except:
            pass
        time.sleep(10)
        self.start()

    def ping(self):
        if self.connected:
            _LOGGER.debug("Sending ping")
            self.connected = False
            self.send_command('ping')
            self.ping_event = self.ping_scheduler.enter(10, 1, self.ping)
            self.ping_scheduler.run(False)
        else:
            _LOGGER.debug("Ping: Calling restart")
            self.restart()

    def send_command(self, command):
        try:
            self.ws.send(command)
        except:
            _LOGGER.info("Sending command failed, restarting")
            self.restart()

    def send_node_command(self, node, attribute, target_value):
        self.send_command("PUT:nodes/{}/attributes/{}?target_value={}".format(node.id, attribute.id, target_value))

    def play_homeegram(self, id):
        self.send_command("PUT:homeegrams/{}?play=1".format(id))

    def _run_event_loop(self):
        token = self.cube.get_token()
        self.ws = websocket.WebSocketApp("ws://{}:7681/connection?access_token={}".format(self.hostname, token),
                                         subprotocols=["v2"],
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.on_open = self.on_open
        self.ws.run_forever()

    def on_message(self, message):
        if message == 'pong':
            self.connected = True
            _LOGGER.debug("pong received")
            return
        try:
            parsed = json.loads(message)
        except Exception as e:
            _LOGGER.error("Failed to parse json: " + str(e))
            return
        if "all" in parsed:
            if "nodes" in parsed['all']:
                for node in parsed['all']['nodes']:
                    self._parse_node(node)
            if "groups" in parsed['all']:
                for group in parsed['all']['group']["groups"]:
                    self.groups.append(Group(group))

        if "node" in parsed:
            self._parse_node(parsed['node'])

        if "attribute" in parsed:
            attribute = Attribute(parsed["attribute"])
            if attribute.node_id in self._callbacks:
                for callback in self._callbacks[attribute.node_id]:
                    callback(None, attribute)
        else:
            pass

    def _parse_node(self, parsed):
        node = Node(parsed)
        self._nodes[node.id] = node

        if node.id in self._callbacks:
            for callback in self._callbacks[node.id]:
                callback(node, None)

    def on_error(self, error):
        _LOGGER.error("Websocket Error %s", error)
        self.restart()

    def on_close(self):
        pass

    def on_open(self):
        _LOGGER.info("Websocket opened")
        self.connected = True
        self.ping()
