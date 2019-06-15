

from .context import crdf_serializer

import unittest


from rdflib import Namespace, Literal, URIRef,RDF
from crdf_serializer import ObjectDecorator, BindDecorator, graph
from rdflib.namespace import DC, FOAF


# exemplo do rdflib
class Person:
    nick = FOAF.nick
    name = FOAF.name
    email = FOAF.mbox

    @ObjectDecorator(FOAF.Person, None) # blank node
    @BindDecorator("dc", DC)
    @BindDecorator("foaf", FOAF)
    def __init__ (self, name, nick, email):
        self.nick = Literal(nick, lang="foo")
        self.name = Literal (name)
        self.email = URIRef(email) 

p = Person ("Donna Fales","donna", "mailto:donna@example.org")


class TestSelect(unittest.TestCase):
    def test(self):
        for person in graph(p).subjects(RDF.type, FOAF.Person):
            for mbox in graph(p).objects(person, FOAF.mbox):
                self.assertTrue(mbox == URIRef("mailto:donna@example.org"))