#!/usr/bin/env python3

import requests
from dnslib import *
from base64 import urlsafe_b64encode

class dscan:
	def __init__(self, provider='cloudflare'):
		self.wire = False
		self.provider = provider
		self.headers = {
			'Accept': 'application/dns-json'
		}

		if not self.provider in ["adguard", "cloudflare", "google", "quad9"]:
			self.provider = "cloudflare"
		
		if self.provider in ['adguard']:
			self.wire = True
		
		providers = {
			'adguard': 'https://dns.adguard.com/dns-query',
			'cloudflare': "https://cloudflare-dns.com/dns-query",
			'google': 'https://dns.google.com/resolve',
			'quad9': 'https://dns.quad9.net/dns-query'
		}
		self.base = providers[self.provider]

	def single(self, domain, rrtype='AAAA'):
		if not rrtype.upper() in ['A', 'AAAA', 'CNAME', 'MX', 'NS', 'TXT']:
			return "You provided an invalid rrtype: {}".format(rrtype)

		try:
			if self.wire:
				question = DNSRecord.question(domain, rrtype)
				question = urlsafe_b64encode(question.pack()).decode()

				data = requests.get(
					"{}?dns={}".format(self.base, question),
					headers=self.headers
				)
			else:
				data = requests.get(
					"{}?name={}&type={}".format(self.base, domain, rrtype),
					headers=self.headers
				)

			if data.status_code == 200:
				results = []
				if self.wire:
					record = DNSRecord.parse(data.content)
					for r in record.rr:
						results.append(str(r.rdata))
					return results
				else:
					data = data.json()
					if data['Status'] == 0:
						try:
							for answer in data['Answer']:
								results.append(answer['data'])
							return results
						except:
							return []
			return []
		except:
			return []