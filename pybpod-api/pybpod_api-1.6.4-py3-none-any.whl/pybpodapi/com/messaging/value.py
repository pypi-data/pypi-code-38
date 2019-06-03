# !/usr/bin/python3
# -*- coding: utf-8 -*-
from confapp import conf
from pybpodapi.com.messaging.base_message import BaseMessage


class ValueMessage(BaseMessage):
	"""
	Stderr message from the server process

	.. seealso::

		:py:class:`pybpodgui_plugin.com.messaging.board_message.BoardMessage`

	"""
	MESSAGE_TYPE_ALIAS = 'VAL'
	MESSAGE_COLOR = (240,0,0)


	def __init__(self, value_name, value, host_timestamp=None):
		"""

		:param value_name:
		:param value:
		:param host_timestamp:
		"""		
		super(ValueMessage, self).__init__(value_name, host_timestamp)
		self._value = value


	@property
	def value_name(self): return self.content

	@property
	def value(self): return self._value


	def tolist(self):
		return [
			self.MESSAGE_TYPE_ALIAS, 
			str(self.pc_timestamp), 
			self.host_timestamp,
			None,
			self.value_name,
			self.value
		]

	@classmethod
	def fromlist(cls, row):
		"""
		Returns True if the typestr represents the class
		"""
		obj = cls(
			int(row[4]),
			row[5],
			float(row[2]) if row[2] else None
		)
		obj.pc_timestamp = dateutil.parser.parse(row[1])

		return obj
	