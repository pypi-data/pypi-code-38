#!/usr/bin/env python3

import requests
from dnslib import *
from base64 import urlsafe_b64encode
from .util import Utils

class Abusix:
	def __init__(self, address, provider="https://cloudflare-dns.com/dns-query"):
		self.base = Utils(address)
		self.provider = provider
		self.reverse = "{}.abuse-contacts.abusix.zone".format(self.base._reverse())

	def lookup(self):
		try:
			question = DNSRecord.question(self.reverse, 'TXT')
			question = urlsafe_b64encode(question.pack()).decode()

			data = requests.get(
				"{}?dns={}".format(self.provider, question),
				headers={
					'Accept': 'application/dns-message'
				}
			)

			if data.status_code == 200:
				record = DNSRecord.parse(data.content)
				for r in record.rr:
					return list(set(str(r.rdata).replace('"', '').split(',')))
		except:
			return []

class BGPView:
	def __init__(self, address):
		self.base = Utils(address)

	def lookup_ip(self):
		try:
			asn = []
			data = requests.get(
				"https://api.bgpview.io/ip/{}".format(self.base.address)
			)
			if data.status_code == 200:
				d = data.json()

				if d['status'] == "ok":
					for p in d['data']['prefixes']:
						asn.append(p['asn']['asn'])
				return list(set(asn))
		except:
			return []

	def lookup(self):
		try:
			asn = self.lookup_ip()
			
			if len(asn) > 0:
				for a in asn:
					data = requests.get(
						"https://api.bgpview.io/asn/{}".format(a)
					)

					if data.status_code == 200:
						contacts = []
						d = data.json()

						if d['status'] == "ok":
							for e in ['email_contacts', 'abuse_contacts']:
								for c in d['data'][e]:
									contacts.append(c.strip())

						return list(set(contacts))
		except:
			return []

class Kahtava:
	def __init__(self, address, provider="http://adam.kahtava.com/services/whois.json?query="):
		self.base = Utils(address)
		self.provider = provider

	def lookup(self):
		try:
			data = requests.get(
				"{}{}".format(self.provider, str(self.base.address))
			)
			if data.status_code == 200:
				contacts = []
				try:
					d = data.json()
					for entity in ["AbuseContact", "AdministrativeContact", "TechnicalContact"]:
						contacts.append(d['RegistryData'][entity]['Email'].strip())
					return list(set(contacts))
				except:
					return []
		except:
			return []

class NoticeAndAction:
	def __init__(self, address, provider="https://noticeandaction.com/resources/php/lookup.php?host="):
		self.base = Utils(address)
		self.provider = provider

	def lookup(self):
		try:
			data = requests.get(
				"{}{}".format(self.provider, str(self.base.address))
			)
			if data.status_code == 200:
				try:
					d = data.json()
					return list(set(d['lookup']['abuseEmail'].split(',')))
				except:
					return []
		except:
			return []

class TeamCymru:
	def __init__(self, address, provider="https://cloudflare-dns.com/dns-query"):
		self.base = Utils(address)
		self.provider = provider

		if self.base._class() == 4:
			self.reverse = "{}.origin.asn.cymru.com".format(self.base._reverse())
		if self.base._class() == 6:
			self.reverse = "{}.origin6.asn.cymru.com".format(self.base._reverse())

	def lookup(self):
		try:
			question = DNSRecord.question(self.reverse, 'TXT')
			question = urlsafe_b64encode(question.pack()).decode()

			data = requests.get(
				"{}?dns={}".format(self.provider, question),
				headers={
					'Accept': 'application/dns-message'
				}
			)

			if data.status_code == 200:
				record = DNSRecord.parse(data.content)
				for r in record.rr:
					d = str(r.rdata).replace('"', '').split('|')
					return {
						'asn': d[0].strip().split(','),
						'cidr': d[1].strip(),
						'country': d[2].strip(),
						'rir': d[3].strip(),
						'date': d[4].strip()
					}
		except:
			return []