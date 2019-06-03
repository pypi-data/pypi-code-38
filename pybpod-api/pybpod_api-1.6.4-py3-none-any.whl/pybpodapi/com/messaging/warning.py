# !/usr/bin/python3
# -*- coding: utf-8 -*-

from pybpodapi.com.messaging.base_message import BaseMessage

class WarningMessage(BaseMessage):
	
	""" Message that represents an error """

	MESSAGE_TYPE_ALIAS = 'warning'	
	MESSAGE_COLOR = (255,100,0)
