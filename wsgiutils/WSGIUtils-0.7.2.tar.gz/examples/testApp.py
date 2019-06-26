""" testApp

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
		
"""
# WSGI Test application
from wsgiutils import SessionClient, wsgiAdaptor, wsgiServer
import logging, time

logging.basicConfig()
root = logging.getLogger()
root.setLevel (logging.DEBUG)

class TestApp:
	def requestHandler (self, request):
		# This is a multi-threaded area, we must be thread safe.
		session = request.getSession()
		if (session.has_key ('lastRequestTime')):
			lastRequest = session ['lastRequestTime']
		else:
			lastRequest = None
		thisTime = time.time()
		session ['lastRequestTime'] = thisTime
		# Use some templating library to generate some output
		if (lastRequest is None):
			request.sendContent ("<html><body><h1>The first request!</h1></body></html>", "text/html")
		else:
			request.sendContent ("<html><body><h1>The time is %s, last request was at %s</h1></body></html>" % (str (thisTime), str (lastRequest)), "text/html")

class CalcApp:
	""" A simple calculator app that uses a username/password of 'user/user' and demonstrates forms.
	"""
	def requestHandler (self, request):
		# Authenticate the user
		username = request.getUsername()
		password = request.getPassword()
		if (username is None or username != 'user'):
			request.sendUnauthorisedBasic ("Calculator")
			return
		if (password is None or password != 'user'):
			request.sendUnauthorisedBasic ("Calculator")
			return

		# We have a valid user, so get the form entries
		formData = request.getFormFields()
		try:
			firstValue = float (formData.getfirst ('value1', "0"))
			secondValue = float (formData.getfirst ('value2', "0"))
		except:
			# No valid numbers, try again
			self.displayForm(request, 0)
			return
		# Display the sum
		self.displayForm (request, firstValue + secondValue)
		return

	def displayForm (self, request, sumValue):
		request.sendContent ("""<html><body><h1>Calculator</h1>
								<h2>Last answer was: %s</h2>
								<form name="calc">
									<input name="value1" type="text"><br>
									<input name="value2" type="text">
									<button name="Calculate" type="submit">Cal.</button>
								</form>
						</body></html>""" % str (sumValue), "text/html")
		

# We will use a local session client because we are not multi-process
testclient = SessionClient.LocalSessionClient('session.dbm', 'testappid')
testadaptor = wsgiAdaptor.wsgiAdaptor (TestApp(), 'siteCookieKey', testclient)

calcclient = SessionClient.LocalSessionClient ('calcsession.dbm', 'calcid')
calcAdaptor = wsgiAdaptor.wsgiAdaptor (CalcApp(), 'siteCookieKey', calcclient)

# Now place the adaptor in WSGI web container
print "Serving two apps on http://localhost:1066/test.py and http://localhost:1066/calc.py"
server = wsgiServer.WSGIServer (("", 1066), {'/test.py': testadaptor.wsgiHook
													  ,'/calc.py': calcAdaptor.wsgiHook})
server.serve_forever()
