class MerchantCredentials:

	def __init__(self, api_key, api_secret):
		self.api_key = api_key
		self.api_secret = api_secret 

	def get_api_key(self):
		return self.api_key

	def get_api_secret(self):
		return self.api_secret