from os                     import environ
from iiiaihub.__client__    import MemberClient, AlgorithmClient

class dict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

class AIHub(object):
    def __init__(self):
        self.__environment__ = dict({})
        self.__environment__.self_token   = environ.get('AIHUB_SELF_TOKEN', None)
        self.__environment__.user_token   = environ.get('AIHUB_USER_TOKEN', None)
        self.__environment__.original     = environ.get('AIHUB_USER_TOKEN', None)
        self.__environment__.file_url     = environ.get('AIHUB_FILE_URL', 'https://aihub.ifeel.com.tw/__api/file/')
        self.__environment__.gateway_url  = environ.get('AIHUB_GATEWAY_URL', 'https://aihub.ifeel.com.tw/__api/gateway/')

    def addKey(self, environment, key, token):
        if key and token:
            getattr(self, environment)[key] = token

    def client(self, self_token=None):
        if self_token:
            if self.__environment__.self_token :
                raise ValueError('Can not set the self_token in the Algorithm!')
            else:
                self.addKey('__environment__', 'self_token', self_token)
                self.addKey('__environment__', 'user_token', self_token)
                self.addKey('__environment__', 'original', self_token)
                
        if not self.__environment__.self_token :
            raise ValueError('Client must have a token! Please use client(\'token\') to enter the token!')

        client_type = MemberClient if self.__environment__.user_token==self.__environment__.self_token else AlgorithmClient
        return client_type(self.__environment__)
