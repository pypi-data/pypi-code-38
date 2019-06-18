from openapi_client.configuration import Configuration
from openapi_client.api_client import ApiClient

class ClientContext:

	@staticmethod
	def create(creds):
		return ClientContext(creds)

	def __init__(self, creds):
		self.config = Configuration()
		self.client = ApiClient(self.config)
		self.credentials = creds
