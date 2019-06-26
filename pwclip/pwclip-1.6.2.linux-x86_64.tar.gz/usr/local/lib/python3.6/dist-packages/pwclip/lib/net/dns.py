#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""net.dns module"""

try:
	from os import uname
except ImportError:
	from os import environ
	uname = ['', environ['COMPUTERNAME']]

from re import search

from socket import getfqdn, gethostbyaddr, gaierror, herror

def isip(pattern):
	"""return true if input is possibly an ip-address"""
	# return True if "pattern" is RFC conform IP otherwise False
	iplike = r'^(?!0+\.0+\.0+\.0+|255\.255\.255\.255)' \
		r'(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)' \
		r'\.(25[0-5]|2[0-4]\d|[01]?\d\d?)\.(25[0-5]|2[0-4]\d|[01]?\d\d?)$'
	if search(iplike, pattern):
		return True
	return False

def fqdn(name):
	"""get the fully qualified domain name"""
	__fqdn = getfqdn(name) if name else uname()[1]
	if __fqdn:
		return __fqdn
	return name

def askdns(host):
	"""ask dns for ip or name and return answer if ther is one"""
	try:
		dnsinfo = gethostbyaddr(host)
	except (gaierror, herror, TypeError):
		return False
	if isip(host):
		return dnsinfo[0]
	if len(dnsinfo[2]) == 1:
		return dnsinfo[2][0]
	return dnsinfo[2]

def raflookup(host):
	"""reverse and forward lookup function"""
	lookup, reverse = '', ''
	if host:
		lookup = askdns(host)
		if lookup:
			reverse = askdns(lookup)
	return lookup, reverse
