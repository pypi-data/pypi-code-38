#!/usr/bin/env python3

import argparse, os, sys, json
from .abuse import Abuse
from .util import Utils

def main():
	p = argparse.ArgumentParser(description="findabuse.email: CLI")

	p.add_argument("address", nargs=1, help="the IP address to lookup")

	p.add_argument("--json", default=False, action="store_true")
	p.add_argument("--ipinfo", default='', help="if provided, authenticate with ipinfo.io")
	args = p.parse_args()

	# Validation
	try:
		ip = Utils(args.address[0])
	except ValueError:
		print("The address you provided, {}, is not a valid IPv4 / IPv6 address".format(args.address[0]))
		exit()

	# So invalid data gone
	if args.ipinfo == "":
		contacts = Abuse(args.address[0], ipinfo_key=args.ipinfo).lookup()
	else:
		contacts = Abuse(args.address[0]).lookup()

	if args.json:
		print(json.dumps({
			'results': contacts
			})
		)
	else:
		for c in contacts:
			print(c)

if __name__ == '__main__':
	main()