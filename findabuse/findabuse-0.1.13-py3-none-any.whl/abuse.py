#!/usr/bin/env python3

from .providers import Abusix, BGPView, NoticeAndAction
from collections import Counter

class Abuse:
	def __init__(self, address):
		self.address = address

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
			'notice': NoticeAndAction(self.address).lookup()
		}

		contacts = []
		for s in services:
			contacts.extend(services[s])

		return self.remove(self.sort(contacts))