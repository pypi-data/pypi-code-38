import tornado.ioloop
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPRequest
import tornado.httpserver
import tornado.web
from tornado.curl_httpclient import CurlAsyncHTTPClient
import HttpServerWrapper
import HttpClientWrapper
import datetime
import JsonDecoder
import logging

ogger = logging.getLogger(__name__)

class DefaultMsgHandler(tornado.web.RequestHandler):
		def post(self):
			print "Received request from OTT"
			post_body = self.request.body
			print post_body
			msg = JsonDecoder.decodeIncomingMessage(post_body)
			for header in self.request.headers:
				msg.httpHeaders[header] = self.request.headers[header]
			if msg.messageType == "Status":
				print msg.toString()
			else:
				self.onMessage(msg)

		def onMessage(self, msgObj):
			print "default on Mesasge"
			pass
		def onStatus(self, msg):
			pass
		def onError(self):
			pass
		def sendResponse(self, responseCode = 200, headers = {}, content = ""):
			print "sendingResponse", content
			
			for key in headers:
				self.set_header(key, headers[key])
			self.set_status(responseCode)
			self.flush()

class DefaultResponseHandler:
		def handleResponse(self,response):
			print "reason", response.reason
			print "code", response.code
			print "error", response.error
			print "body", response.body
			print "headers", response.headers
			print "headers", response.request
			print "Not Implemented"

class DefaultHttpServerWrapper(HttpServerWrapper.HttpServerWrapper):
		def __init__(self, handler_class=DefaultMsgHandler):
			self.handler_class = handler_class
		
		def startHttpServer(self, port, webhook):
			print "starting http server"
			application = tornado.web.Application([(webhook, self.handler_class),], )
			server = tornado.httpserver.HTTPServer(application)
			server.listen(port)
			tornado.ioloop.IOLoop.current().start()
	
		def registerCallBack(self, callBack, timer, *args):
			print "registeringCallback"
			tornado.ioloop.IOLoop.current().add_timeout(datetime.timedelta(seconds=timer),callBack, args)

class DefaultHttpClientWrapper(HttpClientWrapper.HttpClientWrapper):
		def __init__(self, response_handler=DefaultResponseHandler):
			self.client = CurlAsyncHTTPClient()
			self.responseHandler = response_handler()

		def sendRequest(self, url = "",  body = "", headers ={}):
			print "sending Request"
			print body
			aReq = HTTPRequest(url=url, method = "POST", body=body, headers=headers)
			self.client.fetch(aReq, self.responseHandler.handleResponse)

		def registerCallBack(self, callBack, timer, *args, **kwargs):
			print "registeringCallback"
			tornado.ioloop.IOLoop.current().add_timeout(datetime.timedelta(seconds=timer),callBack, *args, **kwargs)

		def startTimer(self, callBack, timer, *args, **kwargs):
			print "registeringCallback"
			tornado.ioloop.IOLoop.current().add_timeout(datetime.timedelta(seconds=timer),callBack, *args, **kwargs)
'''
		def registerCallBack(self, callBack, timer, **kwargs):
			print "registeringCallback"
			tornado.ioloop.IOLoop.current().add_timeout(datetime.timedelta(seconds=timer),callBack, **kwargs)
'''
