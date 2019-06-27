import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import secrets


class GetToken:
	def __init__(self, client_id):
		self.client_id = client_id
		self.redirect_uri = None
		self.retries  = Retry(total=3,
                             backoff_factor=1,
                             status_forcelist=[500, 502, 503, 504])

	# The following is the OAuth2 authorization endpoint URI.
	def authorize(self):
		api_url = 'https://notify-bot.line.me/oauth/authorize'
		self.state = secrets.token_hex(nbytes=10)

		# Request
		session = requests.Session()
		session.mount('https://', HTTPAdapter(max_retries=self.retries))

		response = session.post(
                url=api_url,
                data={'response_type': 'code',
        		    	  'client_id': self.client_id,
        		    	  'redirect_uri': self.redirect_uri,
        		    	  'scope': 'notify',
        		    	  'state': self.state},
                timeout=3)

		if response.status_code != 200:
			return response
        
		self.code = response.get('code')

		return response



	# The OAuth2 token endpoint.
	# Never save client_secret
	def oauthtoken(self, client_secret, code=None):
		api_url = 'https://notify-bot.line.me/oauth/token'
		if code==None:
			print('Try authorize, or input the code')
			return False
		self.code = code

		# Request
		session = requests.Session()
		session.mount('https://', HTTPAdapter(max_retries=self.retries))

		response = session.post(
			url=api_url,
		    data={'grant_type': 'authorization_code',
		    	  'code': self.code,
		    	  'redirect_uri': self.redirect_uri,
		    	  'client_id': self.client_id,
		    	  'client_secret': client_secret},
	        timeout=3
	    )

		self.token = response.get('access_token')

		return self.token
