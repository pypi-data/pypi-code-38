import bottle
from bottle import request, route, Bottle
from .serializer import Serializer

class Api():
    '''
    Central object of AJAS, runs the actual webserver. 
    Allows to add resolvers to paths and automatically serializes their return values.
    Allows to add Blocks for purposes like authentication, versioning etc.
    '''
    def __init__(self):
        self.resolvers_get = {}
        self.resolvers_post = {}
        self.serializer = Serializer()
        self.app = Bottle()
        self.app.route('<path:path>', method="GET", callback=self.get_callback)
        self.app.route('<path:path>', method="POST", callback=self.post_callback)
        self.blocks = []

    
    def add_block(self, block):
        self.blocks.append(block)


    def add_get_resolver(self, path, resolver):
        '''
        path: String => URL-path
        resolver: Function => resolver function with the signature res(header, query)
        '''
        self.resolvers_get[path] = resolver
    
    def add_post_resolver(self, path, resolver):
        '''
        path: String => URL-path
        resolver: Function => resolver function with the signature res(header, query)
        '''
        self.resolvers_post[path] = resolver

    def get_callback(self, path):
        '''
        Internal method
        Calls the specific resolver for the paths and serializes the return value
        '''
        query = request.query.dict
        for i in query:
            query[i] = query[i][0]
        for i in self.blocks:
            if i.prefix == path[:len(i.prefix)]:
                return self.serializer.serialize(i.resolver_get(path[len(i.prefix):], request.headers, query))
        return self.serializer.serialize(self.resolvers_get[path](request.headers, query))
    
    def post_callback(self, path):
        '''
        Internal method
        Calls the specific resolver for the paths and serializes the return value
        '''
        query = request.forms.dict
        for i in query:
            query[i] = query[i][0]
        for i in self.blocks:
            if i.prefix == path[:len(i.prefix)]:
                return self.serializer.serialize(i.resolver_post(path[len(i.prefix):], request.headers, query))
        return self.serializer.serialize(self.resolvers_post[path](request.headers, query))

    def run(self, host, port, server='wsgiref'):
        '''
        Runs the webserver which hosts the Api.
        host: String => IP-Adress which the server listens to, use "0.0.0.0" for all
        port: int => Port on which the server listens
        server: String => Server system which AJAS should use, look up on the bottle framework for the server options https://bottlepy.org/docs/dev/deployment.html#server-options
        '''
        self.app.run(host = host, port = port, server = server)