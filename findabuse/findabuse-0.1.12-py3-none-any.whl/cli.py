#!/usr/bin/env python3

import argparse, os, sys, json
from .abuse import Abuse
from .util import Utils

def main():
	p = argparse.ArgumentParser(description="findabuse.email: CLI")

	p.add_argument("address", nargs=1, help="the IP address to lookup")
	p.add_argument("--json", default=False, action="store_true")

	args = p.parse_args()

	# Validation
	try:
		ip = Utils(args.address[0])
	except ValueError:
		print("The address you provided, {}, is not a valid IPv4 / IPv6 address".format(args.address[0]))
		exit()

	# So invalid data gone
	try:
		contacts = Abuse(args.address[0]).lookup()
		if args.json:
			print(json.dumps({
				'results': contacts
				})
			)
		else:
			for c in contacts:
				print(c)
	except:
		print("We encountered an error while processing your request")
		exit()

if __name__ == '__main__':
	main()