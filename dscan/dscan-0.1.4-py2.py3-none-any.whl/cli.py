#!/usr/bin/env python3

import os, sys, argparse, json
import requests
from .dscan import dscan

PROVIDERS = [
	"adguard",
	"appliedprivacy",
	"cleanbrowsing-family",
	"cloudflare",
	"commons.host",
	"dnswarden",
	"dnswarden-adblock",
	"google",
	"powerdns",
	"quad9"
]

def main():

	parser = argparse.ArgumentParser()

	# IO
	parser.add_argument("--input", '-i', help="path to list of domains (in plain text)")
	parser.add_argument("--output", '-o', help="path to output")

	# Records
	parser.add_argument("--rrtype", "-r", help="rrtype to collate", default="AAAA")

	# Modes
	parser.add_argument("--single", "-s", help="single domain mode", action="store_true")
	parser.add_argument("--provider", "-p", choices=PROVIDERS, help="dns provider to use", default="cloudflare")
	
	# Domain (in single mode)
	parser.add_argument("domain", help="domain name (single mode only)", default="", nargs="?")
	
	# Verbose mode
	parser.add_argument("--verbose", "-v", help="increase output verbosity", action="store_true")
	args = parser.parse_args()

	if args.single:
		if args.domain == "":
			print("You must provide a domain name in --single mode (e.g --single cloudflare.com)")
			exit()
		scan = dscan(args.provider)
		res = scan.single(args.domain, args.rrtype)
		print("\n".join(res))
	
	if args.input and args.output:
		domains = []

		with open(args.input, 'r') as f:
			for d in f.readlines():
				domains.append(d.strip())
			f.close()

		output = {}
		for d in domains:
			output[d] = single(d, args.rrtype)
		
		with open(args.output, 'w') as f:
			f.write(json.dumps(output))
			f.close()
		
if __name__ == '__main__':
	main()