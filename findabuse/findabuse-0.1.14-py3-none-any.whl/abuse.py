#!/usr/bin/env python3

from .providers import Abusix, BGPView, IPInfo, NoticeAndAction
from collections import Counter

class Abuse:
	def __init__(self, address, **kwargs):
		self.address = address
		self.kwargs = {}
		for name, content in kwargs.items():
			self.kwargs[name] = content

	def sort(self, data):
		contacts = []
		for contact, count in Counter(data).most_common():
			contacts.append(contact)
		return list(set(filter(None, contacts)))

	def remove(self, data):
		contacts = []
		blacklist = [
			'apnic.net'
		]
		for contact in data:
			if not contact in blacklist and not contact.split('@')[1] in blacklist:
				contacts.append(contact)
		return contacts

	def lookup(self):
		services = {
			'abusix': Abusix(self.address).lookup(),
			'bgpview': BGPView(self.address).lookup(),
			'ipinfo': IPInfo(self.address, key=self.kwargs['ipinfo_key']).lookup(),
			'notice': NoticeAndAction(self.address).lookup()
		}

		contacts = []
		for s in services:
			try:
				contacts.extend(services[s])
			except TypeError:
				pass
		return self.remove(self.sort(contacts))