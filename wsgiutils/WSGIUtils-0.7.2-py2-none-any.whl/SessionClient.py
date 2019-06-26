""" SessionClient

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
		
		Clients that provide Session services.
"""

import socket, xdrlib, struct, cPickle, random, time
import anydbm
import threading
import logging

class Session (dict):
	def __init__ (self, sessionID):
		dict.__init__ (self)
		self.sessionID = sessionID
		self.lastAccessed = time.time()
		
	def getLastAccessed (self):
		return self.lastAccessed
		
	def getSessionID (self):
		return self.sessionID
	
def getNewSessionID ():
	return str (random.randint (0, 99000000000)) + str (time.time())
	
class LocalSessionClient (object):
	def __init__ (self, dbFileLocation, cookieName, sessionLifeSpan = 3600):
		self.lifeSpan = sessionLifeSpan
		self.cookieName = cookieName
		self.log = logging.getLogger ("LocalSessionClient")
		self.dbLock = threading.Lock()
		self.db = anydbm.open (dbFileLocation, 'c')
		
	def getSession (self, cookies):
		cookieValue = None
		if (cookies.has_key (self.cookieName)):
			cookieValue = cookies [self.cookieName].value
			self.log.info ("Found session ID %s" % cookieValue)
		else:
			self.log.info ("No %s cookie found." % self.cookieName)
			# Nothing to load, no session present.
		if (cookieValue is None):
			sessID = getNewSessionID ()
			cookies [self.cookieName] = sessID
			return Session (sessID)
		
		self.dbLock.acquire()
		if (self.db.has_key (cookieValue)):
			pickledSessionData = self.db [cookieValue]
			self.dbLock.release()
		else:
			self.dbLock.release()
			self.log.warn ("Session for ID %s was not found!" % str (cookieValue))
			sessID = getNewSessionID ()
			cookies [self.cookieName] = sessID
			return Session(sessID)
			
		self.log.info ("Session for ID %s found in db." % str (cookieValue))
		sessionData = cPickle.loads (pickledSessionData)
		if ((time.time() - sessionData.getLastAccessed()) > self.lifeSpan):
			self.log.info ("Session has expired - cleaning up old data.")
			sessionData.clear()
		return sessionData
		
	def saveSession (self, session):
		self.dbLock.acquire()
		session.lastAccessed = time.time()
		self.db [session.getSessionID()] = cPickle.dumps (session)
		self.db.sync()
		self.dbLock.release()
		
	def closeClient (self):
		self.db.sync()
		self.db.close()
		self.db = None

class SessionServerClient (object):
	""" The session server client is a multi-thread safe factory class which 
		generates Session objects for use in a web application.
	"""
	def __init__ (self, socketLocation, cookieName, sessionLifeSpan = 3600):
		self.socketLocation = socketLocation
		self.lifeSpan = sessionLifeSpan
		self.cookieName = cookieName
		self.log = logging.getLogger ("SessionServerClient")
		self.socketLock = threading.Lock()
		self.sessionServerSocket = None
		self.connectToServer()
		
	def connectToServer (self):
		self.socketLock.acquire()
		try:
			if (self.sessionServerSocket is not None):
				self.log.info ("Found old socket, attempting to close.")
				oldSock = self.sessionServerSocket
				self.sessionServerSocket = None
				oldSock.close()
				self.log.debug ("Close succedded")
		except Exception, e:
			self.log.warn ("Error attempting to close old socket (%s) carrying on." % str (e))
			
		try:
			self.log.info ("Attempting to connect to session server listening on unix socket %s" % self.socketLocation)
			self.sessionServerSocket = socket.socket (socket.AF_UNIX, socket.SOCK_STREAM)
			self.sessionServerSocket.connect (self.socketLocation)
			self.log.info ("Connection to session server established!")
		except Exception, e:
			self.log.error ("Unable to connect to session server: %s" % str (e))
			self.sessionServerSocket = None
		self.socketLock.release()
	
	def getSession (self, cookies):
		cookieValue = None
		if (cookies.has_key (self.cookieName)):
			cookieValue = cookies [self.cookieName].value
			self.log.info ("Found session ID %s" % cookieValue)
		else:
			self.log.info ("No %s cookie found." % self.cookieName)
			# Nothing to load, no session present.
		if (cookieValue is None):
			sessID = getNewSessionID ()
			cookies [self.cookieName] = sessID
			return Session (sessID)
		
		msg = xdrlib.Packer()
		msg.pack_string ("GET")
		msg.pack_string (cookieValue)
		msg = msg.get_buffer()
		msgLen = struct.pack ('!l', len (msg))
		# Must get the lock at this stage!
		try:
			self.socketLock.acquire()
			self.log.info ("Sending GET message to server.")
			self.sessionServerSocket.sendall (msgLen)
			self.sessionServerSocket.sendall (msg)
			# Get the response
			self.log.info ("Waiting for response.")
			msgLen = struct.unpack ('!l', self.sessionServerSocket.recv (4))[0]
			rawmsg = self.sessionServerSocket.recv (msgLen)
			# Can now release the lock
			self.socketLock.release()
		except Exception, e:
			# Something went wrong talking to the session server.
			self.socketLock.release()
			self.log.error ("Error communicating with the session server (%s), trying to re-connect." % str (e))
			self.connectToServer()
			# Return a new session with the old session ID
			return Session(cookieValue)
			
		msg = xdrlib.Unpacker (rawmsg)
		msgType = msg.unpack_string()
		self.log.info ("Response is message type: %s" % msgType)
		if (msgType == 'NOTFOUND'):
			self.log.warn ("Session for ID %s was not found!" % str (cookieValue))
			sessID = getNewSessionID ()
			cookies [self.cookieName] = sessID
			return Session(sessID)
		elif (msgType == 'FOUND'):
			self.log.info ("Session for ID %s found in server." % str (cookieValue))
			pickledSessionData = msg.unpack_string()
			# The pickled object 
			# Now de-pickle the list of name-value pairs.
			sessionData = cPickle.loads (pickledSessionData)
			if ((time.time() - sessionData.getLastAccessed()) > self.lifeSpan):
				self.log.info ("Session has expired - cleaning up old data.")
				sessionData.clear()
			return sessionData
		else:
			self.log.error ("Unsupported message command respones from session server: " + str (msgType))
			raise Exception ("Unsupported message command respones from session server: " + str (msgType))
		
	def saveSession (self, session):
		msg = xdrlib.Packer()
		msg.pack_string ("SET")
		session.lastAccessed = time.time()
		msg.pack_string (session.getSessionID())
		msg.pack_string (cPickle.dumps (session))
		msg = msg.get_buffer()
		msgLen = struct.pack ('!l', len (msg))
		# Must get the lock at this stage!
		try:
			self.socketLock.acquire()
			self.log.info ("Sending SET message to server.")
			self.sessionServerSocket.sendall (msgLen)
			self.sessionServerSocket.sendall (msg)
			# Get the response
			self.log.info ("Waiting for response.")
			msgLen = struct.unpack ('!l', self.sessionServerSocket.recv (4))[0]
			rawmsg = self.sessionServerSocket.recv (msgLen)
			# Can now release the lock
			self.socketLock.release()
		except Exception, e:
			# Something went wrong talking to the session server.
			self.socketLock.release()
			self.log.error ("Error communicating with the session server (%s), trying to re-connect." % str (e))
			self.connectToServer()
			return
		
		msg = xdrlib.Unpacker (rawmsg)
		msgType = msg.unpack_string()
		self.log.info ("Response is message type: %s" % msgType)
		if (msgType == 'OK'):
			self.log.info ("Session saved OK.")
		else:
			self.log.error ("Error saving session!")
			raise Exception ("Error saving session.")
	
	def closeClient (self):
		msg = xdrlib.Packer()
		msg.pack_string ("BYE")
		msg = msg.get_buffer()
		msgLen = struct.pack ('!l', len (msg))
		# Must get the lock at this stage!
		try:
			self.socketLock.acquire()
			self.log.info ("Sending BYE message to server.")
			self.sessionServerSocket.sendall (msgLen)
			self.sessionServerSocket.sendall (msg)
			# Get the response
			self.log.info ("Waiting for response.")
			msgLen = struct.unpack ('!l', self.sessionServerSocket.recv (4))[0]
			rawmsg = self.sessionServerSocket.recv (msgLen)
			self.log.info ("Closing socket connection.")
			self.sessionServerSocket.close()
			self.sessionServerSocket = None
			# Can now release the lock
			self.socketLock.release()
		except Exception, e:
			# Something went wrong talking to the session server.
			self.socketLock.release()
			self.log.error ("Error communicating with the session server (%s), trying to re-connect." % str (e))
			self.connectToServer()
			return
		
