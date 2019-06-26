#!/usr/bin/python
""" 	Copyright (c) 2004 Colin Stewart (http://www.owlfish.com/)
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
		
		Unit test cases.
		
"""

import unittest, os, os.path, sys

from wsgiutils import wsgiAdaptor

ENV = {'wsgi.errors': sys.stderr, 'PATH_INFO': '/', 'wsgi.url_scheme': 'http'
	  ,'HTTP_HOST': 'localhost'}

class RequestTests (unittest.TestCase):
	def testGoodPath (self):
		dirToTest = os.tempnam()
		pathToTest = os.path.join (dirToTest, "Test File")
		os.mkdir (dirToTest)
		testdata = "This is a test."
		createFile = open (pathToTest, 'w')
		createFile.write (testdata)
		createFile.close()
		
		request = wsgiAdaptor.Request (ENV)
		# Try the good test.
		request.sendFileForPath ("Test%20File", dirToTest)
		self.failUnless (testdata == request.contentValue, "Reading test file failed: %s" % str (request.contentValue))
		# Cleanup
		os.remove (os.path.join (dirToTest, "Test File"))
		os.rmdir (dirToTest)
		
	def testBadPath (self):
		request = wsgiAdaptor.Request (ENV)
		try:
			request.sendFileForPath ("../etc/passwd", "/tmp/")
			self.fail ("Able to read passwd file from /tmp/")
		except:
			pass
	
		