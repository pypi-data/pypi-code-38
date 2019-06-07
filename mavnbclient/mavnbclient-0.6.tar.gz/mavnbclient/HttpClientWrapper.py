from abc import ABCMeta, abstractmethod

class HttpClientWrapper():
		__metaclass__ = ABCMeta

		@abstractmethod
		def sendRequest(self):
			pass
