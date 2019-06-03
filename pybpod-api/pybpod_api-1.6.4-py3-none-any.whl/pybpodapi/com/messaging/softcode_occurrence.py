# !/usr/bin/python3from pybpodapi.com.messaging.base_message import BaseMessage
# -*- coding: utf-8 -*-
import dateutil
from pybpodapi.com.messaging.base_message import BaseMessage


class SoftcodeOccurrence(BaseMessage):
	"""
	Message from board that represents state change (an event)

	:ivar str event_name: name of the event
	:ivar int event_id: index of the event
	:ivar float board_timestamp: timestamp associated with this event (from bpod)

	"""
	MESSAGE_TYPE_ALIAS = 'SOFTCODE'
	MESSAGE_COLOR = (40,30,30)
	
	def __init__(self, softcode, host_timestamp=None):
		"""

		:param event_id:
		:param event_name:
		:param host_timestamp:
		"""		
		super(SoftcodeOccurrence, self).__init__(softcode, host_timestamp)


	
	@property
	def softcode(self): return self.content

