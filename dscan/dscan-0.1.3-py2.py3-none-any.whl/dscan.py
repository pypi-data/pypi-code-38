#!/usr/bin/env python3

import requests
from dnslib import *
from base64 import urlsafe_b64encode

class dscan:
	def __init__(self, provider='cloudflare'):
		self.provider = provider

		if not self.provider in ["adguard", "cloudflare", "google", "quad9"]:
			self.provider = "cloudflare"
		
		providers = {
			'adguard': {
				'url': 'https://dns.adguard.com/dns-query',
				'method': 'wireformat'
			},
			'cleanbrowsing-family': {
				'url': 'https://doh.cleanbrowsing.org/doh/family-filter',
				'method': 'wireformat'
			},
			'cloudflare': {
				'url': 'https://cloudflare-dns.com/dns-query',
				'method': 'wireformat'
			},
			'google': {
				'url': 'https://dns.google.com/resolve',
				'method': 'json'
			},
			'quad9': {
				'url': 'https://dns.quad9.net/dns-query',
				'method': 'wireformat'
			}
		}
		self.base = providers[self.provider]

		if self.base['method'] in ['json']:
			self.headers = {
				'Accept': 'application/dns-json'
			}
		else:
			self.headers = {
				'Accept': 'application/dns-message'
			}

	def single(self, domain, rrtype='AAAA'):
		if not rrtype.upper() in ['A', 'AAAA', 'CNAME', 'MX', 'NS', 'TXT']:
			return "You provided an invalid rrtype: {}".format(rrtype)

		try:
			if self.base['method'] in ['wireformat']:
				question = DNSRecord.question(domain, rrtype)
				question = urlsafe_b64encode(question.pack()).decode()

				data = requests.get(
					"{}?dns={}".format(self.base['url'], question),
					headers=self.headers
				)
			else:
				data = requests.get(
					"{}?name={}&type={}".format(self.base['url'], domain, rrtype),
					headers=self.headers
				)

			if data.status_code == 200:
				results = []
				if self.base['method'] in ['wireformat']:
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