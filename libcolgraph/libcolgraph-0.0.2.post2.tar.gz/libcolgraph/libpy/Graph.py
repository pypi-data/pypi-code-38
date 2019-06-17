#!/usr/bin/env python3

# import graph_tool as gt
from .Vertex import *
from pathlib import Path
import typing
from tqdm import tqdm
import networkx as nx
from utils import mathtools
from matplotlib import pyplot as plt


class Graph(object):#(gt.Graph):
    '''
    The OG graph class
    '''
    n = None
    vertices = None

    def __init__(self, *args, **kwargs):
        # super().__init__(*args, **kwargs, directed=False)
        self.vertices = dict()
        self.n = 0


    def __str__(self) -> str:
        '''
        string representation of the graph for print output
        '''
        returnable = ''
        returnable += ('='*64 + '\n')
        returnable += ('Graph class: %s\n' % self.__class__.__name__)
        returnable += ('Graph size: %d\n' % len(self))
        returnable += ('='*64 + '\n')
        # returnable += ('Vertices:\n')
        # for v in self.get_vertices():
        #     returnable += str(v) + '\n'

        return returnable


    def __len__(self) -> int:
        '''
        override len method to get size
        '''
        if self.n:
            return self.n
        return 0


    def __getitem__(self, ID) -> Vertex:
        '''
        override __getitem__ method to get vertex via subscripting
        whose ID is ID
        '''
        return self.get_vertex(ID)


    def load_txt(self, path: typing.Union[str, Path]) -> None:
        '''
        loads a text file containing a description of a graph and constructs
        internal representation of it.
        the text file must have a single line containing |V| followed by
        |V| lines that together make up an adjacency matrix
        '''
        if not isinstance(path, Path):
            path = Path(path)
        with path.open(mode='r') as f:
            for i in range(int(f.readline())):
                self.add_vertex(i)
            for i, line in enumerate(f):
                if i >= self.n: break
                adjacent = [ix for ix, v in enumerate(line.split()) if int(v)]
                self.vertices[i].add_neighbors(*[self.vertices[j]
                                               for j in adjacent])


    def add_vertex(self, id: int=None, name: str=None) -> None:
        '''
        adds new vertex with given id and additional attrs
        '''
        self.vertices[id] = Vertex(id)
        self.vertices[id][NAME] = name
        self.n += 1


    def get_vertex(self, id: int) -> Vertex:
        '''
        returns vertex with supplied ID
        '''
        return self.vertices[id]


    def get_neighbors(self, v: Vertex=None) -> typing.List[Vertex]:
        '''
        '''
        return v.get_neighbors()


    def get_vertices(self) -> typing.Iterable[Vertex]:
        '''
        returns an iterable over vertices (using a generator)
        '''
        for k, v in self.vertices.items():
            yield v


    def get_some_vertex(self) -> Vertex:
        '''
        gets some arbitrary vertex of the graph
        '''
        for v in self.get_vertices():
            return v


    def reset_attrs(self, *attrs: list) -> None:
        '''
        sets the supplied attributes to None for each vertex
        '''
        for v in self.vertices():
            for attr in attrs:
                v[attr] = None


    def draw(self, draw_fn=nx.draw, **kwargs):
        '''
        internal method to draw graph
        '''
        print(self)
        G = nx.Graph()
        # G.add_nodes_from(self.vertices.keys())
        for v in self.get_vertices():
            G.add_node(v)
            for nbr in self.get_neighbors(v):
                G.add_edge(v, nbr)
        draw_fn(G, **kwargs)


class BaseGraph(Graph):
    '''
    derived 'Base' class to hold a regular BaseGraph
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def get_color(self, coloring: int=0, v: Vertex=None, k: int=1) -> int:
        '''
        returns the color of vertex v in the given coloring
        '''
        # return mathtools.convert_base(coloring, k, len(self))[v[ID]]
        return (coloring // k ** (len(self)-v[ID]-1)) % k


    def is_valid_coloring(self, coloring: int, k: int) -> bool:
        '''
        given a coloring as an integer (bit-string in base k), determines
        if it is valid or not
        '''
        for v in self.get_vertices():
            vcol = self.get_color(coloring=coloring, v=v, k=k)
            neighbors = v.get_neighbors()
            for n in neighbors:
                if vcol == self.get_color(coloring=coloring, v=n, k=k):
                    return False

        return True


    def get_colorings(self, k: int, verbose: bool=True) -> typing.Iterable[int]:
        '''
        generates all possible colorings of the graph for k colors
        '''
        for coloring in tqdm(range(k ** len(self)), disable=not verbose,
                             desc='generating colorings for k=%d' % k):
            if self.is_valid_coloring(coloring, k):
                yield coloring
            else:
                continue


    def build_coloring_graph(self, k: int=None, verbose: bool=True) -> Graph:
        '''
        generates and returns a ColoringGraph object for the current
        BaseGraph object
        '''
        colgraph = ColoringGraph(k)
        colgraph.base = self
        for i, coloring in enumerate(self.get_colorings(k, verbose)):
            colgraph.add_vertex(i, name=coloring)

        return colgraph


class ColoringGraph(Graph):
    '''
    specifically to hold a ColoringGraph of a BaseGraph
    '''
    base = None
    k = None

    def __init__(self, k: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.k = k


    def add_vertex(self, id: int=None, name: int=None) -> None:
        '''
        adds new vertex with given id and additional attrs
        '''
        self.vertices[name] = ColoringVertex(name)
        # self.vertices[name][ID] = name
        self.vertices[name][NAME] = name
        self.vertices[name][COLORS] = self.k
        self.vertices[name].graph = self
        self.n += 1


    def get_neighbors(self, v: ColoringVertex) -> set:
        '''
        gets the neighbors of ColoringVertex v
        '''
        all = v.get_possible_neighbors(len(self.base))
        all = set(all)
        valid = all.intersection(self.vertices.keys())
        for vertex in map(lambda name: self[name], valid):
            yield vertex


    def draw_vertex_surroundings(self, v):
        raise NotImplementedError



def Tarjans(g: Graph):
    '''
    '''
    root = g.get_some_vertex()
