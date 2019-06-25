from iiiaihub.__helper__       import requestsHelper
from six.moves.urllib.parse import quote
from requests               import post, delete, patch
from json                   import dumps

class Collection(object):
    def __init__(self, client, collection_name):
        self.client          = client
        self.collection_name = collection_name

    def create(self):
        return requestsHelper(
            func=post,
            headers={'Authorization' : self.client.environment.user_token, 'Self' : self.client.environment.self_token, 'Original' : self.client.environment.original, 'Content-Type' : 'application/json'},
            url=('{}{}'.format(self.client.environment.file_url, 'folder/')),    
            data=dumps({'folder_name':self.collection_name})
        )

    def delete(self):
        return requestsHelper(
            func=delete,
            headers={'Authorization' : self.client.environment.user_token, 'Self' : self.client.environment.self_token, 'Original' : self.client.environment.original, 'Content-Type' : 'application/json'},
            url=('{}{}'.format(self.client.environment.file_url, 'folder/')),
            data=dumps({'folder_name':self.collection_name})
        )

    def rename(self, new_collection_name):
        return requestsHelper(
            func=patch, 
            headers={'Authorization' : self.client.environment.user_token, 'Self' : self.client.environment.self_token, 'Original' : self.client.environment.original, 'Content-Type' : 'application/json'},
            url=('{}{}'.format(self.client.environment.file_url, 'folder/')),
            data=dumps({'folder_name':self.collection_name, 'new_folder_name':new_collection_name})
        )


