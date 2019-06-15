from rdflib.namespace import RDF, FOAF
from rdflib import URIRef, BNode, Literal
from rdflib import Graph
from rdflib import Namespace

def get_class_vars(cl):
    return {key:value for key, value in cl.__dict__.items() if not key.startswith('__') and not callable(key)}

class ObjectDecorator():

    def __init__(self, node_type, node_url):
        self.node_type = node_type
        self.node_url = node_url


    def link_nodes (self, object):
        class_vars = get_class_vars(type(object))
        for k,v in object.__dict__.items():
            if (k != "_uri" and (isinstance(v, Literal) or isinstance(v, URIRef))) :
                object.g.add( (object._uri, class_vars[k], v) )

    def __call__(self, fun, *args, **kwargs):
        def inner_func(*args, **kwargs):
            args[0].g = Graph()
            obj = fun(*args, **kwargs)
            if (self.node_url):
                args[0]._uri = URIRef(self.node_url + args[0].id)
            else:
                args[0]._uri = BNode()
            args[0].g.add( (args[0]._uri, RDF.type, self.node_type) )
            self.link_nodes(args[0])
            return obj

        return inner_func

def graph (value):
    if isinstance(value, list):
        gtotal = Graph()
        for o in value:
            gtotal = gtotal + o.g
        return gtotal
    else:
        return value.g