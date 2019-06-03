# !/usr/bin/python3
# -*- coding: utf-8 -*-

import logging, dateutil
from pybpodapi.com.messaging.base_message import BaseMessage

logger = logging.getLogger(__name__)


class StateTransition(BaseMessage):
	"""
	Store timestamps for a specific state occurrence of the state machine
	
	:ivar str name: name of the state
	:ivar list(StateDuration) timestamps: a list of timestamps (start and end) that corresponds to occurrences of this state
	"""

	MESSAGE_TYPE_ALIAS = 'TRANSITION'
	MESSAGE_COLOR = (0,200,0)

	def __init__(self, state_name, host_timestamp):
		"""

		:param str name: name of the state
		"""
		super().__init__(state_name, host_timestamp)



	def tolist(self):
		return [
			self.MESSAGE_TYPE_ALIAS, 
			str(self.pc_timestamp), 
			self.host_timestamp,
			None,
			self.content,
			None
		]

	@classmethod
	def fromlist(cls, row):
		"""
		Returns True if the typestr represents the class
		"""
		obj = cls(
			row[4],
			float(row[2]) if row[2] else None
		)
		obj.pc_timestamp = dateutil.parser.parse(row[1])

		return obj


	@property
	def state_name(self): return self.content