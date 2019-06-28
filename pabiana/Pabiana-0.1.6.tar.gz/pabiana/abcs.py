from abc import ABC, abstractmethod
from typing import Any, Callable, Optional, Dict, Tuple, Set

from .utils import Interfaces


class Node(ABC):
	"""Abstract interface implemented by every Pabiana Node.
	
	A Pabiana Node is a type of networking software that can provide different types of Interfaces.
	Other Nodes can connect to these Interfaces.
	
	Attributes:
		name: Unique name of the Node.
		interfaces: IP addresses, ports and optionally host IPs for every Nodes interfaces are stored here.
		time: Internal time of the Node.
	"""
	def __init__(self, name: str, interfaces: Interfaces):
		self.name = name  # type: str
		self.interfaces = interfaces  # type: Interfaces
		self.time = 1  # type: int
	
	def rslv(self, interface: str, name: str=None) -> Tuple[str, int, Optional[str]]:
		"""Return the IP address, port and optionally host IP for one of this Nodes interfaces."""
		if name is None:
			name = self.name
		key = '{}-{}'.format(name, interface)
		host = None
		if 'host' in self.interfaces[key]:
			host = self.interfaces[key]['host']
		return self.interfaces[key]['ip'], self.interfaces[key]['port'], host
	
	@abstractmethod
	def run(self):
		"""Starts the Node. Runs in an infinite loop."""
		pass
	
	@abstractmethod
	def stop(self):
		"""Stops the Node safely."""
		pass


class Area(Node):
	"""Abstract interface implemented by every Pabiana Area.
	
	A Pabiana Area is a special type of Node.
	It can provide one Receiver and multiple Subscriber Interfaces.
	Other Areas could call remote Triggers on and Publish messages to these Interfaces.
	It can process Triggers and messages. It includes time synch mechanisms.

	Attributes:
		clock_name: Unique name of the Clock.
		clock_slot: Name of the publishing Slot of the Clock signal.
		context: Central store of the Areas non-volatile state.
	"""
	def __init__(self, name: str, interfaces: Interfaces):
		super().__init__(name, interfaces)
		self.clock_name = None  # type: str
		self.clock_slots = None  # type: Set[str]
		self.context = {}  # type: dict

	@abstractmethod
	def publish(self, message: dict, slot: str=None):
		"""Publishes a message on the optionally given Slot."""
		pass

	@abstractmethod
	def trigger(self, target: str, trigger: str, parameters: Dict[str, Any]={}):
		"""Calls the specified Trigger of another Area with the optionally given parameters.

		Args:
			target: The name of the target Area.
			trigger: The name of the Trigger.
			parameters: The parameters of the function call.
		"""
		pass

	@abstractmethod
	def scheduling(self, func: Callable) -> Callable:
		"""Registers this function as scheduler (only one). Intended to be used as decorator."""
		pass
	
	# ------------- Trigger processing functions -------------
	
	@abstractmethod
	def register(self, func: Callable) -> Callable:
		"""Registers the function as remote Trigger. Intended to be used as decorator."""
		pass
	
	@abstractmethod
	def comply(self, trigger: str, parameters: Dict[str, Any]={}):  # TODO: args/kwargs?
		"""Registers a request to call the Trigger function with the given parameters during the next round.

		This method should be induced by Areas higher in the hierarchy, to influence this Areas procedures.
		A certain trigger will only be called once in a single round.
		The parameters of the most recent request will be used.
		This method should not be called from within the Area.
		Autoloop requests are given preference.

		Args:
			trigger: The name of the trigger.
			parameters: The parameters of the function call.
		"""
		pass
	
	@abstractmethod
	def autoloop(self, trigger: str, parameters: Dict[str, Any]={}):  # TODO: args/kwargs?
		"""Registers a request to call the Trigger function with the given parameters during the next round.

		A certain trigger will only be called once in a single round.
		The parameters of the most recent request will be used.
		This method is intended to be called from within the Area.

		Args:
			trigger: The name of the trigger.
			parameters: The parameters of the function call.
		"""
		pass
	
	# ------------- Message processing functions -------------
	
	@abstractmethod
	def alteration(self, func: Callable=None, source: str=None, slot: str=None) -> Callable:
		"""Registers the function to be called in the next round after a optionally specified Subscriber message has arrived.

		Intended to be used as decorator.
		Only one function can be registered for a certain source/slot combination.

		Args:
			func: The function to be called.
			source: The optional name of the Area that sent the message.
			slot: The optional Slot from which the message was sent. A source must be given.
		"""
		pass
	
	@abstractmethod
	def process(self, source: str, message: dict, slot: str=None):
		"""Processes the given message. A message should originate from an Area lower in the hierarchy.

		This method should be induced by Areas lower in the hierarchy, to send their results.
		Data processing should be done by alteration functions.
		This method should not be called from within the Area.

		Args:
			source: The name of the Area that sent the message.
			message: The message to be processed.
			slot: The optional Slot from which the message was sent.
		"""
		pass
	
	@abstractmethod
	def alter(self, source: str=None, slot: str=None):
		"""Requests an alteration function to be called in the next round, even if no Subscriber message has arrived.
		
		A certain function will only be called once in a single round.
		This method is intended to be called from within the Area.

		Args:
			source: The source value the desired function was registered with.
			slot: The slot value the desired function was registered with.
		"""
		pass
	
	# ------------- Clock processing functions -------------
	
	@abstractmethod
	def activity(self, func: Callable) -> Callable:
		"""Registers the function to be called if there occurred input during this round.
		
		Only one function can be set.
		This method is intended to be used as a decorator.
		"""
		pass
	
	@abstractmethod
	def pulse(self, func: Callable) -> Callable:
		"""Registers the function to be called at the end of every round.
		
		Only one function can be set.
		This method is intended to be used as a decorator.
		"""
		pass
	
	@abstractmethod
	def proceed(self):
		"""Initiates the next round of this Areas procedures. Requested functions will be called.
		
		This method should be induced by a syncing Node, like a common Clock.
		This method should not be called from within the Area.
		"""
		pass
