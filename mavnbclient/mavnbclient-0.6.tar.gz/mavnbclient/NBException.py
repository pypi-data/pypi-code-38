#!/usr/bin/python

class NBException(Exception):
	def __init__(self, reason, howToFix):
		self.errorReason = reason
		self.howToFix = howToFix

class JsonEncodeException(NBException):
	def __init__(self, reason, howToFix, msgObject):
		self.msgObject = msgObject
		super(JsonEncodeException, self).__init__(reason, howToFix)

class JsonDecodeException(NBException):
	def __init__(self, reason, howToFix, msgJson):
		self.msgJson = msgObject
		super(JsonDecodeException, self).__init__(reason, howToFix)

class OAuthException(NBException):
	def __init__(self, reason, howToFix, response):
		super(OAuthException, self).__init__(reason, howToFix)
		self.reason = response.reason
		self.status = response.status
		self.headers = response.getheaders()
		self.body = response.read()
