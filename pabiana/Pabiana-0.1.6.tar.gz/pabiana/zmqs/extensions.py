import json
import logging
from typing import Any, Dict

import zmq

from ..abcs import Node
from .utils import Socket, Context


logger = logging.getLogger(__name__)


class Publisher:
	def __init__(self, node: Node, context: Context):
		self._node = node  # type: Node
		self._zmq = context  # type: Context
		self._publisher = None  # type: Socket
	
	def publish(self, message: dict, slot: str=None):
		if self._publisher is None:
			ip, port, host = self._node.rslv('pub')
			self._publisher = self._zmq.socket(zmq.PUB)
			self._publisher.bind('tcp://{}:{}'.format(host or ip, port))
		message = json.dumps(message)
		self._publisher.send_multipart([(slot or '').encode('utf-8'), message.encode('utf-8')])
		logger.debug('Message published at "%s"', slot)


class Pusher:
	def __init__(self, node: Node, context: Context):
		self._node = node  # type: Node
		self._zmq = context  # type: Context

	def trigger(self, target: str, trigger: str, parameters: Dict[str, Any]={}):
		ip, port, host = self._node.rslv(name=target, interface='rcv')
		pusher = self._zmq.socket(zmq.PUSH)  # type: Socket
		pusher.connect('tcp://{}:{}'.format(ip, port))
		parameters['trigger'] = trigger
		pusher.send_json(parameters)
		pusher.close()
		logger.debug('Trigger "%s" of "%s" called', trigger, target)
