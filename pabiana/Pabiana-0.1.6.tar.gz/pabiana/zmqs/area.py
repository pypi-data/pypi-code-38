import json
import logging
from typing import Any, Callable, Dict, Optional, Sequence, Set, Iterable

import zmq

from .extensions import Publisher, Pusher
from .node import Node
from .utils import caller
from .. import abcs
from ..parsers import init_full, imprint_full
from ..utils import Interfaces


logger = logging.getLogger(__name__)


class Area(Node, abcs.Area):
	"""Class that implements the Pabiana Area interface based on the ZMQ Node class.

	A ZMQ Pabiana Area can provide one Puller (as Receiver) and multiple Subscriber Interfaces.
	Other ZMQ Pabiana Areas could Push Triggers on and Publish messages to these Interfaces.
	"""
	def __init__(self, name: str, interfaces: Interfaces):
		super().__init__(name, interfaces)
		self._schedule_function = caller  # type: Callable

		self._triggers = {'exit': self.stop}  # type: Dict[str, Callable]
		self._demand = {}  # type: Dict[Callable, Dict[str, Any]]
		self._loop = {}  # type: Dict[Callable, Dict[str, Any]]

		self._processors = {}  # type: Dict[Optional[str], Dict[Optional[str], Callable]]
		self._alterations = set()  # type: Set[Callable]
		self._altered = set()  # type: Set[Callable]
		
		self._active_function = None  # type: Callable
		self._pulse_function = None  # type: Callable

		self.publish = Publisher(self, self._zmq).publish
		self.trigger = Pusher(self, self._zmq).trigger

	def publish(self, message: dict, slot: str = None): pass

	def trigger(self, target: str, trigger: str, parameters: Dict[str, Any]={}): pass

	def scheduling(self, func: Callable) -> Callable:
		def combined(*args, **kwargs):
			caller(*func(*args, **kwargs))
		self._schedule_function = combined
		return func
	
	def subscribe(self, clock_name: str=None, clock_slots: Iterable[str]=None, subscriptions: Dict[str, Any]={}):
		"""Subscribes this Area to the given Areas and optionally given Slots. Must be called before the Area is run.

		Args:
			clock_name: The name of the Area that is used as synchronizing Clock.
			clock_slots: The slots of the Clock relevant to this Area.
			subscriptions: A dictionary containing the relevant Areas names as keys and optionally the Slots as values.
		"""
		for area in subscriptions:  # type: str
			init_full(self, area, subscriptions[area])
			subscriptions[area] = {'slots': subscriptions[area]}

		if clock_name is not None:
			self.clock_name = clock_name
			self.clock_slots = clock_slots
			subscriptions[clock_name] = {'slots': clock_slots, 'buffer-length': 1}
		self.setup(puller=True, subscriptions=subscriptions)
	
	def _process(self, interface: int, message: Sequence[str], source: str=None):
		if interface == zmq.PULL:
			message = json.loads(message[0])
			trigger_name = message['trigger']
			del message['trigger']
			self.comply(trigger_name, message)
		else:
			if source == self.clock_name:
				logger.log(5, 'Tick')
				self.proceed()
			else:
				slot = message[0]
				message = json.loads(message[1])
				self.process(source, message, slot)
	
	# ------------- Trigger processing functions -------------
	
	def register(self, func: Callable) -> Callable:
		self._triggers[func.__name__] = func
		return func
	
	def comply(self, trigger: str, parameters: Dict[str, Any]={}):
		try:
			logger.debug('Trigger call: "%s"', trigger)
			func = self._triggers[trigger]
			self._demand[func] = parameters
		except KeyError:
			logger.warning('Unavailable Trigger called')
		
	def autoloop(self, trigger: str, parameters: Dict[str, Any]={}):
		func = self._triggers[trigger]
		self._loop[func] = parameters
	
	# ------------- Message processing functions -------------
	
	def alteration(self, func: Callable=None, source: str=None, slot: str=None) -> Callable:
		def decorator(internal_func):
			if source not in self._processors:
				self._processors[source] = {}
			self._processors[source][slot] = internal_func
			return func
		if func:
			return decorator(func)
		return decorator
	
	def process(self, source: str, message: Dict, slot: str=None):
		try:
			imprint_full(self, source, message, slot)
			func = None
			if None in self._processors:
				func = self._processors[None][None]
			if source in self._processors:
				if slot in self._processors[source]:
					func = self._processors[source][slot]
				elif None in self._processors[source]:
					func = self._processors[source][None]
			if func is not None:
				self._alterations.add(func)
			logger.debug('Subscriber Message from "%s" - "%s"', source, slot)
		except KeyError:
			logger.debug('Unsubscribed Message from "%s" - "%s"', source, slot)
		
	def alter(self, source: str=None, slot: str=None):
		self._altered.add(self._processors[source][slot])
	
	# ------------- Clock processing functions -------------
	
	def activity(self, func: Callable) -> Callable:
		self._active_function = func
		return func
	
	def pulse(self, func: Callable) -> Callable:
		self._pulse_function = func
		return func
	
	def proceed(self):
		looped = None
		if self._loop:
			self._demand.update(self._loop)
			looped = set(self._loop)
			self._loop.clear()
		altered = None
		if self._altered:
			self._alterations.update(self._altered)
			altered = self._altered.copy()
			self._altered.clear()
		if self._demand or self._alterations:
			self._schedule_function(self._demand, self._alterations, looped=looped, altered=altered)
			if self._active_function is not None:
				self._active_function()
			self._demand.clear()
			self._alterations.clear()
		if self._pulse_function is not None:
			self._pulse_function()
		self.time += 1
