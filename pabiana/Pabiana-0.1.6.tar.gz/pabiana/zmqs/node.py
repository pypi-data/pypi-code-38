import logging
import signal
from abc import abstractmethod
from typing import Any, Callable, Dict, Iterable, Sequence

import zmq

from .utils import Context, decoder, Poller, Socket
from .. import abcs
from ..utils import Interfaces


logger = logging.getLogger(__name__)


class Node(abcs.Node):
	"""Abstract class that implements the Pabiana Node interface based on the ZMQ library.

	A ZMQ Pabiana Node can provide one Puller and multiple Subscriber Interfaces.
	Other ZMQ Pabiana Nodes could Push and Publish messages to these Interfaces.
	"""
	def __init__(self, name: str, interfaces: Interfaces):
		super().__init__(name, interfaces)
		self.routine = None  # type: Callable
		self._goon = None  # type: bool
		self._zmq = zmq.Context.instance()  # type: Context
		self._poller = zmq.Poller()  # type: Poller

		self._subscribers = {}  # type: Dict[Socket, str]
	
	def setup(self, puller: bool=None, subscriptions: Dict[str, Any]={}):
		"""Sets up this Node with the specified Interfaces before it is run.

		Args:
			puller: Indication if a Puller Interface should be created.
			subscriptions: Collection of the Subscriber Interfaces to be created and their Slots.
		"""
		if puller:
			puller = self._zmq.socket(zmq.PULL)
			ip, port, host = self.rslv('rcv')
			puller.bind('tcp://{}:{}'.format(host or ip, port))
			self.poll(puller)
		if subscriptions:
			for publisher in subscriptions:  # type: str
				self.add(publisher, subscriptions[publisher].get('slots'), subscriptions[publisher].get('buffer-length'))
			logger.info('Listening to %s', {
				k: (1 if subscriptions[k].get('slots') is None else len(subscriptions[k].get('slots')))
				for k in subscriptions
			})

	def add(self, publisher: str, slots: Iterable[str]=None, buffer_length=None):
		subscriber = self._zmq.socket(zmq.SUB)  # type: Socket
		# if buffer_length is not None:
		# 	subscriber.set_hwm(buffer_length)
		ip, port, host = self.rslv(name=publisher, interface='pub')
		subscriber.connect('tcp://{}:{}'.format(ip, port))
		if slots is None:
			slots = ['']
		for slot in slots:  # type: str
			subscriber.subscribe(slot)
		self._subscribers[subscriber] = publisher
		self.poll(subscriber)

	def poll(self, socket: Socket):
		self._poller.register(socket, zmq.POLLIN)
	
	def run(self, timeout: int=1000, linger: int=1000):
		self._goon = True
		signal.signal(signal.SIGINT, self.stop)
		try:
			while self._goon:
				socks = self._poller.poll(timeout)
				for sock, event in socks:
						self._process(sock.socket_type, decoder(sock.recv_multipart()), self._subscribers.get(sock))
				if self.routine is not None:
					self.routine()
		finally:
			self._zmq.destroy(linger=linger)
			logger.debug('Context destroyed')
			logging.shutdown()

	@abstractmethod
	def _process(self, interface: int, message: Sequence[str], source: str = None):
		pass
	
	def stop(self, *args, **kwargs):
		self._goon = False
