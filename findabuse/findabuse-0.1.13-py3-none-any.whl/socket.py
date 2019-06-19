#!/usr/bin/env python3

import argparse, os, sys, socket, select, redis
from .abuse import Abuse

def main():
	p = argparse.ArgumentParser(description="findabuse.email: DNS resolver")

	# redis server settings
	p.add_argument("--redis", "-r",
		default=os.getenv("REDIS_URL", ""),
	)

	# dns server settings
	p.add_argument("--port", "-p",
		type=int,
		default=5000,
		metavar="<port>",
		help="Server port (default:53)"
	)
	p.add_argument("--address", "-a",
		default="127.0.0.1",
		metavar="<address>",
		help="Listen address (default:all)"
	)
	args = p.parse_args()

	if not args.redis == "":
		r = redis.from_url(args.redis)

	CONNECTION_LIST = []	# list of socket clients
	RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
		
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# this has no effect, why ?
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_socket.bind((args.address, args.port))
	server_socket.listen(10)

	# Add server socket to the list of readable connections
	CONNECTION_LIST.append(server_socket)

	print("Server started on port: {}".format(args.port))

	while 1:
		# Get the list sockets which are ready to be read through select
		read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[])

		for sock in read_sockets:
			
			#New connection
			if sock == server_socket:
				sockfd, addr = server_socket.accept()
				CONNECTION_LIST.append(sockfd)
				print("Client ({}) connected".format(addr))
			#Some incoming message from a client
			else:
				# Data recieved from client, process it
				try:
					data = sock.recv(RECV_BUFFER)
					if data:
						try:
							addr = data.decode('utf-8').replace('\r\n', '')
						except UnicodeDecodeError:
							pass

						if r.get(addr):
							data = r.get(addr).decode("utf-8").split(',')
						else:
							try:
								data = Abuse(addr).lookup()
								r.set(addr, ",".join(data))
							except:
								data = []

						res = ','.join(data)
						msg = "{}\r\n".format(res).encode()
						sock.send(msg)
				
				# client disconnected, so remove from socket list
				except:
					try:
						print("Client (%s, %s) is offline" % addr)
					except TypeError:
						pass
					sock.close()
					CONNECTION_LIST.remove(sock)
					continue
		
	server_socket.close()

if __name__ == '__main__':
	main()