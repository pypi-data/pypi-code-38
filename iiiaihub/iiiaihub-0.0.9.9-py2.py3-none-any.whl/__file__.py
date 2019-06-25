from iiiaihub.__helper__       import requestsHelper
from warnings               import warn
from six.moves.urllib.parse import quote
from requests               import get, put, delete
from json                   import dumps

class File(object):

    def __init__(self, client):
        self.client = client
        self.file_name = None
        self.collection_name = None

    def checkExist(self, **parameter):
        check_dict = {
            'file_name': ValueError('Please enter your file name.'),
            'self_file_name': ValueError('Please use .fileName() to set your filename.'),
            'collection_name': ValueError('Please enter your folder name.'),
            'self_collection_name': ValueError('Please use .collection() to set your folder name.'),
            'data_path': ValueError('Please enter your file path.'),
            'binary_data': ValueError('Data cannot be null.')}
        for key, value in parameter.items():
            if not value : raise check_dict.get(key, ValueError('Missing value!'))
        return True

    def getFile(self, data_path):
        self.checkExist(data_path=data_path)
        return requestsHelper(
            func=get,
            headers={'Authorization' : self.client.environment.user_token, 'Self' : self.client.environment.self_token, 'Original' : self.client.environment.original},
            url=('{}{}'.format(self.client.environment.file_url, 'file_management/')),
            params={'file_path':quote(data_path)}
        )

    def putFile(self, binary_data):
        file_info = {}
        if self.checkExist(binary_data=binary_data, self_file_name=self.file_name) : file_info.update({'filename':self.file_name})
        if self.client.user_client and self.checkExist(self_collection_name=self.collection_name) : file_info.update({'folder_name':self.collection_name})
        return requestsHelper(
            func=put,
            headers={'Authorization' : self.client.environment.user_token, 'Self' : self.client.environment.self_token, 'Original' : self.client.environment.original},
            url=('{}{}'.format(self.client.environment.file_url, 'file_management/')),
            data=file_info,        
            files={'file':binary_data}
        )

    def fileName(self, file_name=None):
        if self.checkExist(file_name=file_name) : self.file_name = file_name
        return self

    def deleteFile(self, data_path):
        self.checkExist(data_path=data_path)
        return requestsHelper(
            func=delete,
            headers={'Authorization' : self.client.environment.user_token, 'Self' : self.client.environment.self_token, 'Original' : self.client.environment.original, 'Content-Type' : 'application/json'},
            url=('{}{}'.format(self.client.environment.file_url, 'file_management/')),                     
            data=dumps({'file_path':data_path})
        )

    def collection(self, collection_name=None):
        if self.client.user_client and self.checkExist(collection_name=collection_name): 
            self.collection_name = collection_name
        else:
            warn('Algorithm cannot use .collection()', category=RuntimeWarning)
        return self




