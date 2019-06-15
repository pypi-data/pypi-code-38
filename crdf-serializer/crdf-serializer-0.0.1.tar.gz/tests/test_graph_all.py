

from .context import crdf_serializer

import unittest


from rdflib import Namespace, Literal, URIRef
from crdf_serializer import ObjectDecorator, BindDecorator, graph
from rdflib.namespace import DC, FOAF

vcard = Namespace('https://www.w3.org/2006/vcard/ns#') #Trazendo uma nova ontologia
n = Namespace("http://linkedscience.org/teach/ns#")

class Curso ():

    # os nomes dessas variaveis de classe, precisam ser os mesmos das de instancia
    title = n.courseTitle
    image = vcard.hasPhoto

    @ObjectDecorator(n.Course, "http://lud.ufma.br/course/")
    @BindDecorator("teach", n)
    @BindDecorator("vcard", vcard)
    def __init__(self, id, title):
        self.id = id
        self.title = Literal(title)
        self.image = URIRef('urlimg')
 



class TestGraphs(unittest.TestCase):
    def test(self):
        c1 = Curso("1","Computação")
        c2 = Curso("2", "Mecanica")
        g = graph([c1,c2])
        self.assertTrue((URIRef('http://lud.ufma.br/course/1'), None, None) in g) # computação
        self.assertTrue((URIRef('http://lud.ufma.br/course/2'), None, None) in g) # mecanica
