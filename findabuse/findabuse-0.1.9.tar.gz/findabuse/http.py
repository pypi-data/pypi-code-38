#!/usr/bin/env python3

import argparse, os, sys, time, copy, redis, json
from bottle import route, request, response, redirect, default_app, view, template, static_file
from .abuse import Abuse

def set_content_type(fn):
	def _return_json(*args, **kwargs):
		response.headers['Content-Type'] = 'application/json'
		if request.method != 'OPTIONS':
			return fn(*args, **kwargs)
	return _return_json

def enable_cors(fn):
	def _enable_cors(*args, **kwargs):
		response.headers['Access-Control-Allow-Origin'] = '*'
		response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
		response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

		if request.method != 'OPTIONS':
			return fn(*args, **kwargs)
	return _enable_cors

@route('/api/v1/<ip>', method=('OPTIONS', 'GET'))
@enable_cors
@set_content_type
def lookup(ip):
	global r

	output = {
		"results": {},
		"results_info": {}
	}

	addresses = ip.split(',')

	for a in addresses:
		addr = a.strip()

		if r.get(addr):
			contacts = r.get(addr).decode('utf-8').split(',')
		else:
			contacts = Abuse(addr).lookup()
			r.set(addr, ",".join(contacts))

		output['results'][addr] = {
			'contacts': contacts
		}

	output['results_info']['count'] = len(output['results'])
	return json.dumps(output)

def main():
	p = argparse.ArgumentParser(description="findabuse.email: API Server")

	# redis server settings
	p.add_argument("--redis", "-r",
		default=os.getenv("REDIS_URL", ""),
	)

	# dns server settings
	p.add_argument("--port", "-p",
		type=int,
		default=os.getenv("PORT", 5000),
		metavar="<port>",
		help="Server port (default: 5000)"
	)
	p.add_argument("--address", "-a",
		default=os.getenv("HOST", "127.0.0.1"),
		metavar="<address>",
		help="Listen address (default: localhost)"
	)
	args = p.parse_args()

	if not args.redis == "":
		global r
		r = redis.from_url(args.redis)

	try:
		app = default_app()
		app.run(host=args.address, port=args.port, server='tornado')
	except:
		print("Unable to start server on {}:{}".format(args.address, args.port))
		exit()

if __name__ == '__main__':
	main()