from .api import Api
from .exceptions import AuthException

class Block(Api):
    '''
    Object to seperate different resolvers from each other.
    Can be used for versioning or for using different types of authentication.
    '''
    def __init__(self, prefix, authenticator = None):
        '''
        prefix: String => prefix which should be in front of all paths in this block
        auth: Authenticator => Authenticator object. Must inherit from the Authenticator class
        '''
        super().__init__()
        self.prefix = prefix
        self.authenticator = authenticator
        self.app = None
        self.blocks = None
        self.run = None
        self.add_block = None

    def resolver_get(self, path, headers, query):
        if self.authenticator is not None:
            if self.authenticator.authenticate(path, headers, query):
                return self.resolvers_get[path](headers, query)
            else:
                raise AuthException("Path " + path + " requires authentication")
        else:
            return self.resolvers_get[path](headers, query)

    def resolver_post(self, path, headers, query):
        if self.authenticator is not None:
            if self.authenticator.authenticate(path, headers, query):
                return self.resolvers_post[path](headers, query)
            else:
                raise AuthException("Path " + path + " requires authentication")
        else:
            return self.resolvers_post[path](headers, query)