import networkx as nx
from .egfuncs import *
import plotly.graph_objs as go
import copy

class Edge:
    def __init__(self, G, dim):
        self.G = G
        self.dim = dim
        self.settings = []
        self.default_color = 'black'
        self.cmin = None
        self.cmax = None
        self.wmin = None
        self.wmax = None
        self.default_min_width = 0.5
        self.default_max_width = 5

    def load(self, df, from_col, to_col):
        for index, row in df.iterrows():
            f = row[from_col]
            t = row[to_col]
            mydict = row.to_dict()
            mydict.pop(from_col, None)
            mydict.pop(to_col, None)
            self.add(f, t, mydict)

    def add(self, from_node, to_node, attributes=None):
        """
           Add edges to the graph.
           Params:
               from_node: initial node
               to_node: destination node
               attributes (optional): dicionary with keys and its corresponding values
        """
        self.G.add_edge(from_node, to_node)
        if attributes is not None:
            for k, v in attributes.items():
                self.G.edges[(from_node,to_node)][k]=v

    def get_min_max(self, attribute):
        try:
            min = 10e10
            max = -10e10
            for g in self.G.edges:
                if self.G.edges[g][attribute] < min:
                    min = self.G.edges[g][attribute]
                if self.G.edges[g][attribute] > max:
                    max = self.G.edges[g][attribute]
        except:
            raise
        return min, max

    def get_cmin_cmax(self, attribute):
        self.cmin, self.cmax = self.get_min_max(attribute)

    def get_wmin_wmax(self, attribute):
        self.wmin, self.wmax = self.get_min_max(attribute)

    def get_2d_trace(self, color_col, width_col):
        settings = []
        trace_default = go.Scatter(
            x=[],
            y=[],
            line=dict(
                width=self.default_min_width,
                color=self.default_color,
            ),
            hoverinfo='none',
            mode='lines'
        )
        trace = copy.deepcopy(trace_default)
        for edge in self.G.edges():
            x0, y0 = self.G.node[edge[0]]['pos']
            x1, y1 = self.G.node[edge[1]]['pos']
            trace['x'] = tuple([x0, x1, None])
            trace['y'] = tuple([y0, y1, None])
            trace['name'] = edge[0] + '-' + edge[1]
            if color_col == None:
                color = self.default_color
            else:
                nvalue = self.G.edges[edge][color_col]
                pvalue = (nvalue - self.cmin)/(self.cmax-self.cmin)
                color = get_color(pvalue)[1]

            if width_col == None:
                width = self.default_min_width
            else:
                nvalue = self.G.edges[edge][width_col]
                pvalue = self.default_min_width + (nvalue - self.wmin)/(self.wmax-self.wmin)*self.default_max_width
                width = pvalue
            trace['line'] = dict(width=width,color=color)
            settings.append(copy.deepcopy(trace))
        return settings

    def get_3d_trace(self, color_col, width_col):
        settings = []
        trace_default = go.Scatter3d(
            x=[],
            y=[],
            z=[],
            line=dict(
                width=self.default_min_width,
                color=self.default_color,
            ),
            hoverinfo='none',
            mode='lines'
        )
        trace = copy.deepcopy(trace_default)
        for edge in self.G.edges():
            x0, y0, z0 = self.G.node[edge[0]]['pos']
            x1, y1, z1 = self.G.node[edge[1]]['pos']

            trace['x'] = tuple([x0, x1, None])
            trace['y'] = tuple([y0, y1, None])
            trace['z'] = tuple([z0, z1, None])
            trace['name'] = edge[0] + '-' + edge[1]
            if color_col == None:
                color = self.default_color
            else:
                nvalue = self.G.edges[edge][color_col]
                pvalue = (nvalue - self.cmin)/(self.cmax-self.cmin)
                color = get_color(pvalue)[1]

            if width_col == None:
                width = self.default_min_width
            else:
                nvalue = self.G.edges[edge][width_col]
                pvalue = self.default_min_width + (nvalue - self.wmin)/(self.wmax-self.wmin)*self.default_max_width
                width = pvalue
            trace['line'] = dict(width=width,color=color)
            settings.append(copy.deepcopy(trace))
        return settings

    def set_attribute(self, color_col, width_col):
        if color_col is not None:
            self.get_cmin_cmax(color_col)
        if width_col is not None:
            self.get_wmin_wmax(width_col)
        if self.dim == 3:
            self.settings = self.get_3d_trace(color_col, width_col)
        else:
            self.settings = self.get_2d_trace(color_col, width_col)
