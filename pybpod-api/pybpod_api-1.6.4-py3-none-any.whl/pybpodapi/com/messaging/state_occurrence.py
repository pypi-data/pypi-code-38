# !/usr/bin/python3
# -*- coding: utf-8 -*-

import logging, dateutil
from pybpodapi.com.messaging.base_message import BaseMessage

logger = logging.getLogger(__name__)


class StateOccurrence(BaseMessage):
	"""
	Store timestamps for a specific state occurrence of the state machine
	
	:ivar str name: name of the state
	:ivar list(StateDuration) timestamps: a list of timestamps (start and end) that corresponds to occurrences of this state
	"""

	MESSAGE_TYPE_ALIAS = 'STATE'
	MESSAGE_COLOR = (0,100,0)

	def __init__(self, state_name, host_timestamp, end_timestamp):
		"""

		:param str name: name of the state
		"""
		super(StateOccurrence, self).__init__(state_name, host_timestamp)

		self.start_timestamp = host_timestamp
		self.end_timestamp   = end_timestamp



	def tolist(self):
		return [
			self.MESSAGE_TYPE_ALIAS, 
			str(self.pc_timestamp), 
			self.start_timestamp,
			self.end_timestamp,
			self.content,
			self.end_timestamp-self.start_timestamp
		]

	@classmethod
	def fromlist(cls, row):
		"""
		Returns True if the typestr represents the class
		"""
		obj = cls(
			row[4],
			float(row[2]) if row[2] else None,
			float(row[3]) if row[3] else None
		)
		obj.pc_timestamp = dateutil.parser.parse(row[1])

		return obj


	@property
	def state_name(self): return self.content