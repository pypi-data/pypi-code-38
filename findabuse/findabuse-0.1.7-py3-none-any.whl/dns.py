#!/usr/bin/env python3

import argparse, os, sys, time, copy, redis
from dnslib import RR
from dnslib.server import DNSServer, DNSHandler, BaseResolver, DNSLogger, RCODE, QTYPE
from .abuse import Abuse

class FixedResolver(BaseResolver):
	def __init__(self, r=None, domain='abuse-contact.findabuse.email'):
		self.domain = domain
		self.r = r

	def resolve(self, request, handler):
		reply = request.reply()
		qname = str(request.q.qname).replace('.{}'.format(self.domain), '')
		qtype = QTYPE[request.q.qtype]

		if qtype in ['TXT']:
			if self.r.get(str(qname)[:-1]):
				contacts = self.r.get(str(qname)[:-1]).decode("utf-8").split(',')
			else:
				try:
					contacts = Abuse(str(qname)[:-1]).lookup()
					self.r.set(str(qname)[:-1], ",".join(contacts))
					rrs = RR.fromZone(". 3600 IN TXT {}".format(",".join(contacts)))
			
					for r in rrs:
						a = copy.copy(r)
						a.rname = qname
						reply.add_answer(a)
				except ValueError:
					reply.header.rcode = getattr(RCODE,'NXDOMAIN')

		else:
			reply.header.rcode = getattr(RCODE,'NXDOMAIN')
		return reply

def main():
	p = argparse.ArgumentParser(description="findabuse.email: DNS resolver")

	# redis server settings
	p.add_argument("--redis", "-r",
		default=os.getenv("REDIS_URL", ""),
	)

	# dns server settings
	p.add_argument("--port", "-p",
		type=int,
		default=53,
		metavar="<port>",
		help="Server port (default:53)"
	)
	p.add_argument("--address", "-a",
		default="",
		metavar="<address>",
		help="Listen address (default:all)"
	)
	p.add_argument("--tcp",
		action='store_true',
		default=False,
		help="TCP server (default: UDP only)"
	)
	p.add_argument("--udplen", "-u",
		type=int,default=0,
		metavar="<udplen>",
		help="Max UDP packet length (default:0)"
	)
	p.add_argument("--log", 
		default="request,reply,truncated,error",
		help="Log hooks to enable (default: +request,+reply,+truncated,+error,-recv,-send,-data)"
	)
	p.add_argument("--log-prefix",
		action='store_true',
		default=False,
		help="Log prefix (timestamp/handler/resolver) (default: False)"
	)
	args = p.parse_args()

	if not args.redis == "":
		r = redis.from_url(args.redis)

	resolver = FixedResolver(r)
	logger = DNSLogger(args.log,args.log_prefix)

	print("Starting Fixed Resolver (%s:%d) [%s]" % (
						args.address or "*",
						args.port,
						"UDP/TCP" if args.tcp else "UDP"))

	if args.udplen:
		DNSHandler.udplen = args.udplen

	udp_server = DNSServer(resolver,
						port=args.port,
						address=args.address,
						logger=logger)
	udp_server.start_thread()

	if args.tcp:
		tcp_server = DNSServer(resolver,
							port=args.port,
							address=args.address,
							tcp=True,
							logger=logger)
		tcp_server.start_thread()

	while udp_server.isAlive():
		time.sleep(1)

if __name__ == '__main__':
	main()
