import requests

class MockserverRequester(object):

	def __init__(self):
		self.mockserver_uri = ''

	def set_mockserver_uri(self, uri):
		self.mockserver_uri = 'http://' + uri

	def request_expectations(self, expectations):
		self.request_reset()
		expectation_uri = self.mockserver_uri + '/mockserver/expectation'
		for expectation in expectations:
			try:
				r = requests.put(expectation_uri, data=expectation.get_json())
			except:
				print(expectation_uri + ' is not a valid uri')

	def request_reset(self):
		reset_uri = self.mockserver_uri + '/mockserver/reset'
		try:
			r = requests.put(reset_uri)
			return r.status_code == requests.codes.ok
		except:
			print(reset_uri + ' is not a valid uri')
		return False
    	
		

		