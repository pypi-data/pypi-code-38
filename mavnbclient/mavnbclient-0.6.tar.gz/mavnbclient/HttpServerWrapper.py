#!/usr/bin/python
from abc import ABCMeta, abstractmethod

class HttpServerWrapper():
		__metaclass__ = ABCMeta

		@abstractmethod
		def startHttpServer(self):
			pass
