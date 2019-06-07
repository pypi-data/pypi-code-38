#!/usr/bin/python

import datetime
from enum import Enum

class Message:
	def __init__(self, messageType = "Text", messageText = "", sender = "", recipient = "", reportsRequired = [], msgId = "", reportType = "None", suggestedChipList = "", suggestedResponse = "", richCard = "", fileJson = ""):
		self.messageType = messageType
		self.messageText = messageText
		self.sender = sender
		self.recipient = recipient
		self.reportsRequired = reportsRequired
		self.msgId = msgId
		self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		self.isDelivered = False
		self.isDisplayed = False
		self.reportType = reportType
		self.fileJson = fileJson
		self.suggestedChipList = suggestedChipList
		self.suggestedResponse = suggestedResponse
		self.richCard = richCard
		self.geoLoc = {}
		self.httpHeaders = {}
		self.callbackUrl = ""
		self.callbackUrlValidity = None
	
	def toString(self):
		string = "Message:"
		string += " messageType = " + self.messageType
		string += " messageText = " + self.messageText
		string += " sender = " + self.sender
		string += " recipient = " + self.recipient
		string += " msgId = " + self.msgId
		string += " timestamp = " + self.timestamp
		string += " reportsRequired = " + str(self.reportsRequired)
		string += " isDelivered = " + str(self.isDelivered)
		string += " isDisplayed = " + str(self.isDisplayed)
		string += " reportType = " + str(self.reportType)
		string += " suggestedChipList = " + self.suggestedChipList
		string += " SuggestedResponse = " + self.suggestedResponse
		string += " RichCard = " + self.richCard
		string += " GeoLoc = " + str(self.geoLoc)
		string += " fileJson = " + str(self.fileJson)
		string += " HttpHeaders = " + str(self.httpHeaders)
		string += " callbackURL = " + str(self.callbackUrl)
		string += " callbackUrlValidity = " + str(self.callbackUrlValidity)
		return string

if __name__ == "__main__":
	msg = Message()
