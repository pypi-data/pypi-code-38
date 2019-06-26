""" SessionServer

		Copyright (c) 2004 Colin Stewart (http://www.owlfish.com/)
		All rights reserved.
		
		Redistribution and use in source and binary forms, with or without
		modification, are permitted provided that the following conditions
		are met:
		1. Redistributions of source code must retain the above copyright
		   notice, this list of conditions and the following disclaimer.
		2. Redistributions in binary form must reproduce the above copyright
		   notice, this list of conditions and the following disclaimer in the
		   documentation and/or other materials provided with the distribution.
		3. The name of the author may not be used to endorse or promote products
		   derived from this software without specific prior written permission.
		
		THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
		IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
		OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
		IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
		INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
		NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
		DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
		THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
		(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
		THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
		
		If you make any bug fixes or feature enhancements please let me know!
		
		A Unix daemon server that provides Session persistence.
"""

import os, logging, threading, Queue, socket, anydbm, xdrlib, struct

# Wire protocol is based on XDR messages.  Each message is precedded by a 4 byte length in network byte order.
# Client can issue a message of two strings, GET, KEY
# OR three strings: SET, KEY, DATA
# Server responds with an XDR message of FOUND, DATA or NOTFOUND
# For set operation return will be OK or ERROR
class Server (object):
	def __init__ (self, addr, dbfile):
		self.addr = addr
		self.dbfile = dbfile
		self.db = anydbm.open (dbfile, 'c')
		self.log = logging.getLogger ("SessionServer")
		self.log.info ("Server init function.")
		
	def runServer (self):
		logging.info ("Starting to serve.")
		self.serve()
		
	def serve (self):
		try:
			listenSocket = socket.socket (socket.AF_UNIX, socket.SOCK_STREAM)
			listenSocket.bind (self.addr)
			listenSocket.listen(2)
			serving = True
		except Exception, e:
			self.log.critical ("Unable to start listening on socket: %s" % str (e))
			serving = False
		while (serving):
			try:
				connSocket, connAddr = listenSocket.accept()
			except Exception, e:
				self.log.error ("Exception occured while waiting for a client: " + str (e))
				self.db.sync()
				self.db.close()
				return
			try:
				self.handleClient (connSocket)
			except Exception, e:
				try:
					self.log.info ("Error handling client (%s), closing socket." % str (e))
					connSocket.close()
				except:
					pass
	
	def handleClient (self, connSocket):
		# Repeated handle incoming messages until the socket goes away.
		serving = 1
		while (serving):
			# Read the message length
			msgLen = struct.unpack ('!l', connSocket.recv (4))[0]
			rawmsg = connSocket.recv (msgLen)
			
			msg = xdrlib.Unpacker (rawmsg)
			msgType = msg.unpack_string()
			
			replymsg = xdrlib.Packer()
			if (msgType == "SET"):
				key = msg.unpack_string()
				value = msg.unpack_string()
				self.log.info ("Saving session ID %s" % key)
				self.db [key] = value
				self.db.sync()
				replymsg.pack_string ("OK")
			elif (msgType == "GET"):
				key = msg.unpack_string()
				if (self.db.has_key (key)):
					self.log.info ("Loading session ID %s" % key)
					value = self.db [key]
					replymsg.pack_string ("FOUND")
					replymsg.pack_string (value)
				else:
					self.log.info ("Session ID %s not found" % key)
					replymsg.pack_string ("NOTFOUND")
			elif (msgType == "BYE"):
				self.db.sync()
				replymsg.pack_string ("OK")
				serving = 0
			else:
				self.log.warn ("Unknown command type: " + msgType)
				replymsg.pack_string ("ERROR")
				replymsg.pack_string ("Unknown command type: " + msgType)
			replymsg = replymsg.get_buffer()
			msgLen = struct.pack ('!l', len (replymsg))
			connSocket.sendall (msgLen)
			connSocket.sendall (replymsg)
		connSocket.close()

def preStartup ():
	try:
		os.remove (SOCKET_ADDR)
	except:
		# No such file, that's OK.
		pass
		
