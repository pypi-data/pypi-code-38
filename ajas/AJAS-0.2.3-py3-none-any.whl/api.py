from .serializer import Serializer
from flask import Flask, request
from gevent.pywsgi import WSGIServer

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
        self.app = Flask(__name__)
        self.app.add_url_rule('/<path:path>', "get", self.get_callback, methods=["GET"])
        self.app.add_url_rule('/<path:path>', "post", self.post_callback, methods=["POST"])
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
        query = request.args
        path = "/" + path
        for i in self.blocks:
            if i.prefix == path[:len(i.prefix)]:
                return self.serializer.serialize(i.resolver_get(path[len(i.prefix):], request.headers.environ, query))
        return self.serializer.serialize(self.resolvers_get[path](request.headers.environ, query))
    
    def post_callback(self, path):
        '''
        Internal method
        Calls the specific resolver for the paths and serializes the return value
        '''
        query = request.form
        path = "/" + path
        for i in self.blocks:
            if i.prefix == path[:len(i.prefix)]:
                return self.serializer.serialize(i.resolver_post(path[len(i.prefix):], request.headers.environ, query))
        return self.serializer.serialize(self.resolvers_post[path](request.headers.environ, query))

    def run(self, host, port, ssl_context = None):
        '''
        Runs the webserver which hosts the Api.
        host: String => IP-Adress which the server listens to, if you want the server to listen to all IPs just give an empty string
        port: int => Port on which the server listens
        '''
        self.app.logger.debug("Server is starting...")
        if ssl_context == None:
            http_server = WSGIServer((host, port), self.app)
        else:
            http_server = WSGIServer((host, port), self.app, keyfile=ssl_context[1], certfile=ssl_context[0])
        http_server.serve_forever()