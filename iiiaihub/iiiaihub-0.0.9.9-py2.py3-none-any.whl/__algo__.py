import urllib
from requests               import post
from json                   import dumps
from iiiaihub.__helper__    import requestsHelper

class Algo(object): 
    def __init__(self, client, algo_url):
        self.client = client
        self.url = algo_url

    def post(self, input_parameters):
        try:
            return requestsHelper(
                func=post,
                headers={'Authorization' : self.client.environment.self_token, 'Original' : self.client.environment.original, 'Content-Type' : 'application/json'},
                url=(self.client.environment.gateway_url),    
                data=dumps({'url':self.url,'input_params':input_parameters})
            )
        except Exception as e:
            raise e