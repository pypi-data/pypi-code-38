from uriDefinitions import KNOWROB_URI
from rdflib.term import URIRef


def get_uri(suffix):
    return URIRef(KNOWROB_URI+"#"+suffix)


def get_suffix_of_uri(uri):
    #http://knowrob.org/kb/knowrob.owl#SUFFIX
    return str(uri.split('#')[1])