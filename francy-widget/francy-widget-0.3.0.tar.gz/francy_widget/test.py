# -*- coding: utf-8 -*-

"""class MyClass:
    a=0
    b: str

o = MyClass()
o
print(o.__dict__)
print(o.a)"""

"""
class GraphNode(dict):
    def __init__(self, **kwargs):
        super(GraphNode, self).__init__([
            ('id', None), ('x', 0), ('y', 0), ('type', None), ('size', None), ('title', ''), ('conjugate', None), ('color', ''),
            ('highlight', None), ('layer', None), ('parent', ''), ('menus', {}), ('messages', {}), ('callbacks', {})
        ], **kwargs)
        to_drop = []
        for k in self.keys():
            if self[k] is None:
                to_drop.append(k)
        for k in to_drop:
            del(self[k])

n = GraphNode()
print(n)
print(type(n).__mro__)

n = GraphNode(title="OK", id="F100")
print(n)
print(type(n).__mro__)"""

from francy_widget import *
import networkx as nx                                                                                                                                                                                                                          
e = [(1, 2), (2, 3), (3, 4)]
G = nx.Graph(e)
app = FrancyApp()
app.set_graph(G)
#print(app.to_dict())
print(app.to_json())
