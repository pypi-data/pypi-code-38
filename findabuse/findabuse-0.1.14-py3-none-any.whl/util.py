#!/usr/bin/env python3

import ipaddress

class Utils:
	def __init__(self, address):
		self.address = address

		# now for validity checks
		self._valid()
		# and now some meta info
		self.address_class = self._class()

	def _class(self):
		return self.address_meta.version

	def _reverse(self):
		return self.address_meta.reverse_pointer.replace('.in-addr.arpa', '').replace('.ip6.arpa', '')

	def _reverse_arpa(self):
		return self.address_meta.reverse_pointer

	def _valid(self):
		try:
			self.address_meta = ipaddress.ip_address(self.address)
		except ValueError:
			raise ValueError("{} does not appear to be a valid IPv4 / IPv6 address".format(self.address))