from typing import Any, Dict

import zmq

from .extensions import Publisher, Pusher
from .utils import Context
from ..abcs import Node
from ..utils import Interfaces


class Runner(Node):
	"""Abstract class to implement Pabiana Nodes with the ability to publish messages and call Triggers based on ZMQ."""
	def __init__(self, name: str, interfaces: Interfaces):
		super().__init__(name, interfaces)
		self._zmq = zmq.Context.instance()  # type: Context
		self.publish = Publisher(self, self._zmq).publish
		self.trigger = Pusher(self, self._zmq).trigger

	def publish(self, message: dict, slot: str = None): pass

	def trigger(self, target: str, trigger: str, parameters: Dict[str, Any]={}): pass
