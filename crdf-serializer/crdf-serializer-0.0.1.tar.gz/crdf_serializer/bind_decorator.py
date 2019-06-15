
from rdflib.namespace import RDF, FOAF
from rdflib import URIRef, BNode, Literal
from rdflib import Graph
from rdflib import Namespace


class BindDecorator ():

    def __init__(self, prefix, namespace):
        self.prefix = prefix
        self.namespace = namespace


    def __call__(self, fun, *args, **kwargs):
        def inner_func(*args, **kwargs):
            args[0].g.bind(self.prefix, self.namespace)
            return fun(*args, **kwargs)
        return inner_func