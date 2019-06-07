from itertools import product

import math
import os
import sys
import tarfile
import tempfile
from collections import OrderedDict, defaultdict
import igraph
import pickle
import pandas
import plotly.graph_objs as go
from plotly.offline import iplot
from tqdm import tqdm

from network_extensions import igraphx
from network_extensions.igraphx.graph_plotly import createFigGraph
from igraphx_simulations import simulations
import colorlover
import logging
from igraphx_simulations.simulations import SIM_METHODS, STANDARD_PROPS

logger = logging.getLogger(__name__)
import numpy as np


class NotCalculatedYetError(Exception):
    pass


class MultiLayerGraph(OrderedDict):
    """
    A multilayer graph describes a complex multi-layer (multi-level) network.
    The graph can consist of bi-partite and non-bipartite layer.

    We assume in this network that all nodes with the *same* label are the same nodes.
    """

    def __init__(self, *args, **kwargs):
        self._multi_layer = None  ##contains the network created by joining the layers into one.
        self._multi_layer_v_attr_name = None
        self._ynws = {}  ##contains a multilayergraph for each year
        # _components = set()
        self._intervall = 1  # number of years merged in one year

        self._fig = None
        self._multilayer_fig = None
        self._ynws_multilayer_figs = None
        self._merged_ynws = None

        super().__init__(*args, **kwargs)

    class BiPartiteGraph(igraph.Graph):
        """
        class for describing bi-partite layers in our network.
        We understand in a number of applications, bi-partite layers as layer which connect different
        no-bipartite networks - usually this networks only consist of one type each.

        e.g. we have a network of institutions and networks of persons. The a bi-partite graph with
        nodes of the types institution and persons combines these two networks.
        """

        def __init__(self, *args, **kwargs):
            """
            Takes all parameters which are allowed for igraph.Graph.
            :param args:
            :param kwargs:
            """
            self._layer_start = None
            self._layer_end = None
            self._typ_field = "typ"  # field which defined the node type which make the networks bipartite
            super().__init__(*args, **kwargs)

        @property
        def startLayer(self) -> str:
            if self._layer_start:
                return self._layer_start

            raise ValueError("not set yet, call: setStartLayer")

        @property
        def endLayer(self) -> str:
            if self._layer_end:
                return self._layer_end

            raise ValueError("not set yet, call: setEndLayer")

        def setStartLayer(self, layer):
            """
            If we understand the bi-partite network as connector we define here one layer.

            :param layer: name of the layer (has to be a layer in the multilayer graph
            :return: None
            """
            self._layer_start = layer

        def setEndLayer(self, layer):
            """
            If we understand the bi-partite network as connector we define here one layer.

            :param layer: name of the layer (has to be a layer in the multilayer graph
            :return: None
            """
            self._layer_end = layer

        def createSimpleLayers(self) -> dict:
            """
            this is a convenient function, we create for each type of nodes in the bi-partite network
            a unconnected network of nodes.
            :return: dict with name of the layer -> graph
            """
            typs = set(self.vs[self._typ_field])

            simpleLayers = {}
            for t in typs:
                ns = self.vs.select(**{self._typ_field: t})
                gr = igraph.Graph()
                for n in ns:
                    gr.add_vertex(**n.attributes())
                simpleLayers[t] = gr

            return simpleLayers

        def biPartiteToAttribute(self, attribute_name: str, layer_start: igraph.Graph = None) -> None:
            """ Creates an attribute for each vertex: The value is the label taken from layer_start it will be attached
            to the vertex in the target.

            e.g. if we have a bipartite Graph with

            Einstein -> physicist
            Planck -> physicist
            Grossmann -> mathematician

            then the function will add "physicist" or "mathematician" as attribute to the layer_start.

            If layer_start is none, then we choose self.


            :param attribute_name: Name of the attribute in the layer
            :param layer_start: (optional) Layer to add the attribute to defaults to self
            """
            if layer_start == None:
                layer_start = self

            layer_start.vs[attribute_name] = ""

            for e in tqdm(self.es):
                s = self.vs["label"][e.source]
                t = self.vs["label"][e.target]
                s_ls = layer_start.vs.select(label=s)
                val = t

                if not s_ls:
                    s_ls = layer_start.vs.select(label=t)
                    val = s

                for s_l in s_ls:

                    if not s_l[attribute_name]:
                        s_l[attribute_name] = val
                    else:
                        # print("%s||%s"%(s_l[attribute_name],val))
                        s_l[attribute_name] = "%s||%s" % (s_l[attribute_name], val)

                if layer_start == self:  ## wenn der Graph selbst benutzt wird dann auch andersherum
                    s = self.vs["label"][e.target]
                    t = self.vs["label"][e.source]

                    if layer_start == None:
                        layer_start = self
                    s_ls = layer_start.vs.select(label=s)
                    val = t
                    if not s_ls:
                        s_ls = layer_start.vs.select(label=t)
                        val = s

                    for s_l in s_ls:
                        if not s_l[attribute_name]:
                            s_l[attribute_name] = val
                        else:
                            s_l[attribute_name] = "%s||%s" % (s_l[attribute_name], val)

        @classmethod
        def load(cls, fn: str, format = None):
            """Load a bipartite graph,
            accepts all formats igraph.load accepts. *doesn't check if the graph is bi-partite!*

            :return: bipartite graph object
            """

            if format:
                tmp_gr = igraph.load(fn,format="graphml")
            tmp_gr = igraph.load(fn)
            gr = cls()
            for n in tmp_gr.vs:
                gr.add_vertex(**n.attributes())
            for n in tmp_gr.es:
                gr.add_edge(n.source, n.target, **n.attributes())

            return gr



    class JoinedMultiLayerGraph(igraph.Graph):
        """
        Describes a graph with has been composed out of different layers. In general, as a result of calling
        :py:func:`generateMultiLayer`
        """

        def __init__(self, *args, **kwargs):
            self._components = set()
            super().__init__(*args, **kwargs)

    class MergedYearNetwork(dict):
        """
        Contains the merged networks. In general created by :py:func:`generateMerged_ynws
        """

        def __init__(self, *args, chooseOnlyNodesInYear=False,
                     mergeattr="label",
                     start_attr="begins",
                     end_attr="ends",
                     **kwargs):
            self.init_params(chooseOnlyNodesInYear, mergeattr, start_attr, end_attr)

            super().__init__()

        def init_params(self, chooseOnlyNodesInYear, mergeattr, start_attr, end_attr):
            self._chooseOnlyNodesInYear = chooseOnlyNodesInYear
            self._mergeattr = mergeattr
            self._start_attr_merge = start_attr
            self._end_attr_merge = end_attr

    class YearNetwork(OrderedDict):
        """
        An extended dictionary which contains a MultiLayerGraphObject for each year.
        """

        def __init__(self):
            self._start = None
            self._end = None
            self._startyear_attr = None
            self._endyear_attr = None
            self._startyear_edge_attr = None
            self._endyear_edge_attr = None
            super().__init__()


        def init_params(self, start, end, startyear_attr, endyear_attr, startyear_edge_attr, endyear_edge_attr):
            self._start = start
            self._end = end
            self._startyear_attr = startyear_attr
            self._endyear_attr = endyear_attr
            self._startyear_edge_attr = startyear_edge_attr
            self._endyear_edge_attr = endyear_edge_attr

        def __getitem__(self, item):  # immitate behaviour of defaultdict
            value = super().get(item, MultiLayerGraph())
            self[item] = value
            return value

        def _update_all(self, ml):
            """
            Convinent function updates a yearnetwork based on new entries in ml.`

            :param ml: a multilayer networks
            :return:
            """
            ml.createYearNetworks(start=self._start,
                                  end=self._end,
                                  startyear_attr=self._startyear_attr,
                                  endyear_attr=self._endyear_attr,
                                  startyear_edge_attr=self._startyear_edge_attr,
                                  endyear_edge_attr=self._endyear_edge_attr,
                                  update=True
                                  )

        def filter_edge_by_vertices(self,start_vertex,end_vertex):
            if isinstance(start_vertex,str):
                start_vertex = {"label":start_vertex}
            if isinstance(end_vertex,str):
                end_vertex = {"label":end_vertex}

            nw = self.copy()
            for y, ynw in self.items():

                if isinstance(ynw, MultiLayerGraph):

                    s_vs = ynw.multi_layer.vs.select(**start_vertex)
                    e_vs = ynw.multi_layer.vs.select(**end_vertex)

                    for s,e in product(s_vs,e_vs):
                        nds = ynw.multi_layer.es.select(_source=s.index,_target=e.index)
                        nds.delete()
                    for v, k in ynw.items():
                        try:
                            s_vs = k.vs.select(**start_vertex)
                            e_vs = k.vs.select(**end_vertex)

                            for s, e in product(s_vs, e_vs):
                                nds = k.es.select(_source=s.index, _target=e.index)
                                nds.delete()
                        except:
                            e = sys.exc_info()
                            logger.debug(e[0], e[1], e[2])
                            logger.warning("""Something (%s) went wrong in year %s. 
                                                         Most likely one of the attributes doesn't exit in this year.""" % (
                            e[0], y))

                else:

                    try:
                        s_vs = ynw.vs.select(**start_vertex)
                        e_vs = ynw.vs.select(**end_vertex)
                        for s, e in product(s_vs, e_vs):
                            nds = ynw.es.select(_source=s.index, _target=e.index)
                            nds.delete()
                            logger.debug("delete: %s" % len(nds))
                    except:
                        e = sys.exc_info()
                        #logger.debug(e[0], e[1], e[2])
                        logger.warning("""Something (%s) went wrong in year %s. 
                                  Most likely one of the attributes doesn't exit in this year.""" % (e[0], y))
            return nw


        def filter_es(self, *args, **kwds):
            """filter all nodes given bei args,kwargs, parameters are the same as in igraph.es.select
            (#TODO still experimental !!)
            :param args: same as for igraph.vs.select
            :param kwds: same as for igraph.vs.select

            :return: MultiLayerGraph without the selected nodes.
            """

            return self._filter("edge",*args,**kwds)

        def filter_vs(self, *args, **kwds):
            """filter all nodes given bei args,kwargs, parameters are the same as in igraph.es.select
            (#TODO still experimental !!)
            :param args: same as for igraph.vs.select
            :param kwds: same as for igraph.vs.select

            :return: MultiLayerGraph without the selected nodes.
            """
            return self._filter("vertex", *args, **kwds)


        def _filter(self, vertex_or_edge, *args, **kwds):
            """filter all nodes given bei args,kwargs, parameters are the same as in igraph.vs.select
            (#TODO still experimental !!)
            :param args: same as for igraph.vs.select
            :param kwds: same as for igraph.vs.select

            :return: MultiLayerGraph without the selected nodes.
            """

            assert vertex_or_edge in ["edge","vertex"], "first parameter has to be 'edge' or 'vertex'"

            if "transform" in kwds:
                transform_func = kwds["transform"]
                del kwds["transform"]

            else:
                transform_func = None

            nw = self.copy()
            for y, ynw in self.items():


                if isinstance(ynw,MultiLayerGraph):
                    try:
                        if transform_func:
                            transform(ynw.multi_layer, transform_func, vertex_or_edge = vertex_or_edge)
                    except NotCalculatedYetError:
                        pass

                    if vertex_or_edge == "vertex":
                        nds = ynw.multi_layer.vs.select(*args, **kwds)
                    else:
                        nds = ynw.multi_layer.es.select(*args, **kwds)

                    nds.delete()
                    for v, k in ynw.items():

                        if transform_func:
                            transform(k, transform_func, vertex_or_edge = vertex_or_edge)
                        try:
                            if vertex_or_edge == "vertex":
                                nds = k.vs.select(*args, **kwds)
                            else:
                                nds = k.es.select(*args, **kwds)
                            nds.delete()
                        except:
                            e = sys.exc_info()
                            logger.debug(e[0], e[1], e[2])
                            logger.warning("""Something (%s) went wrong in year %s. 
                            Most likely one of the attributes doesn't exit in this year.""" % (e[0], y))
                else:

                    try:
                        if transform_func:
                            transform(ynw, transform_func,vertex_or_edge = vertex_or_edge)

                        nds = ynw.vs.select(*args, **kwds)
                        nds.delete()
                    except:
                        e = sys.exc_info()
                        logger.debug(e[0],e[1],e[2])
                        logger.warning("""Something (%s) went wrong in year %s. 
                        Most likely one of the attributes doesn't exit in this year.""" %(e[0],y))
            return nw

    @staticmethod
    def load(fn):
        """
        load multiLayerGraph

        :param fn: Filename

        :return: multiLayerGraph
        """
        with open(fn, "rb") as inf:
            ml = pickle.load(inf)

        return ml

    def save(self, fn):
        """save the multiLayerGraph

        :param fn: filename
        """

        with open(fn, "wb") as outf:
            pickle.dump(self, outf)

    @property
    def multi_layer(self):
        """
        the attached multi-layer graph. Which is one network with all
        nodes and edges of the whole system of graphs.
        Will be generated by calling generateMultiLayer.

        :return:
        """

        if self._multi_layer is None:
            raise NotCalculatedYetError(
                "multi_layer not calculated yet. Please run generateMultiLayer(self, v_attr_name) first!")
        return self._multi_layer

    def addLayerName(self):
        """
        add to each graph in the system a label "layer" to the edges.
        The value is the name of the layer.
        :return:
        """
        for n, gr in self.items():
            gr.es["layer"] = n

    def generateMultiLayer(self, v_attr_name="label", update=False):
        """
        generates one graph which combines all nodes and edges of the multlayer structure.
        :param v_attr_name: (optional) defaults to label. Name of the  attribute of the
        node which uniquely identifies a node.
        :param update: (optional) experimental if set to true it only adds new layers
        :return:
        """
        if not update:
            multi_layer = MultiLayerGraph.JoinedMultiLayerGraph()
            multi_layer.vs[v_attr_name] = ""
        else:
            multi_layer = self._multi_layer
            v_attr_name = self._multi_layer_v_attr_name

        logging.debug("generate multilayer: components before: %s" % multi_layer._components)
        for k, gr in self.items():
            logging.debug("adding: %s" % k)
            if update and k in multi_layer._components:
                logging.debug("already in: %s" % k)
                continue
            if len(gr.vs) > 0:
                multi_layer = igraphx.union(multi_layer, gr, v_attr_name=v_attr_name, typ_field=None)
                multi_layer._components.add(k)
                logging.debug("added: %s" % multi_layer._components)
            else:
                logging.debug("not added (no vertices): %s" % multi_layer._components)
        self._multi_layer = multi_layer
        self._multi_layer_v_attr_name = v_attr_name
        logging.debug("generate multilayer: components now: %s" % multi_layer._components)
        return True

    @property
    def fig(self):
        """The figure object for plotting the multilevel network with iplot/plotly.
        In general, created by calling createFigGraph"""

        if not self._fig:
            raise NotCalculatedYetError("fig not calculated yet, please run createFigGraph ")
        return self._fig

    def createFigGraph(self, title="", hover_field="label", sizes=2, typ_field=None, pos=None):

        fig = createFigGraph(self.multi_layer, title, pos=pos, hover_field=hover_field, sizes=sizes,
                             typ_field=typ_field)
        self._fig = fig

    @property
    def multilayer_fig(self):
        if not self._multilayer_fig:
            raise NotCalculatedYetError("fig not calculated yet, please run createFigLayeredGraph ")
        return self._multilayer_fig

    def calc_sizes(self, func="betweenness", size_mult=20, size_offset=2):
        sizes = {}

        for k, gr in self.items():
            # logging.debug((k,len(gr.es),len(gr.vs)))
            sizes[k] = []

            try:
                vertices = self.multi_layer.vs
            except NotCalculatedYetError:
                logging.error("You need to run generateMultiLayer(self, v_attr_name) first, tu use calc_sizes!")
                raise NotCalculatedYetError(
                    "You need to run generateMultiLayer(self, v_attr_name) first, tu use calc_sizes!")

            for p in vertices:
                try:
                    pc = gr.vs.find(label=p["label"])

                    pc_betw = getattr(pc, func)()
                    gr_betw = getattr(gr, func)()
                    betw = pc_betw / max(gr_betw) * size_mult + size_offset
                except:
                    betw = size_offset
                sizes[k].append(betw)

        return sizes

    def createFigLayeredGraph(self, name, layers, sizes, only_in_layer=False, layer_typ={}):

        layer_graphs = self
        pos_ml = self.multi_layer.layout_fruchterman_reingold()

        poss = {}
        if only_in_layer:
            for l, gr in self.items():
                poss[l] = gr.layout_fruchterman_reingold()

        # generate links between the layers

        Xl = []
        Yl = []
        Zl = []
        for n in self.multi_layer.vs:
            label = n["label"]

            for layer_num in range(0, len(layers) - 1):
                layer = layers[layer_num]
                layer_gr = layer_graphs[layer]

                if layer_typ:  # only relevant if only_in_layer is true
                    if not n["typ"] in layer_typ[layer]:
                        continue

                if only_in_layer:
                    pos = poss[layer]

                else:
                    pos = pos_ml

                if only_in_layer:
                    try:
                        n_tmp = layer_gr.vs.find(label=label)  # TODO search also for typ
                        ni = n_tmp.index
                    except:
                        continue
                else:
                    ni = n.index
                x = pos[ni][0]
                y = pos[ni][1]
                # z = layers.index(layer)
                z = layer

                layer = layers[layer_num + 1]
                layer_gr = layer_graphs[layer]

                if only_in_layer:
                    pos = poss[layer]

                else:
                    pos = pos_ml

                if only_in_layer:
                    try:
                        n_tmp = layer_gr.vs.find(label=label)  # TODO search also for typ
                        ni = n_tmp.index
                    except:
                        continue
                else:
                    ni = n.index

                x1 = pos[ni][0]
                y1 = pos[ni][1]
                # z1 = layers.index(layer)
                z1 = layer

                Xl += [x, x1, None]
                Yl += [y, y1, None]
                Zl += [z, z1, None]

        interlayer_trace = go.Scatter3d(x=Xl,
                                        y=Yl,
                                        z=Zl,
                                        mode='lines',
                                        line=dict(color='rgb(50,20,20)', width=0.2),
                                        # text = texts,
                                        hoverinfo='text'
                                        )

        # print(len (Xl),len(Yl),len(Zl))

        # generate lines in the layers

        Xe = []
        Ye = []
        Ze = []
        for layer in layers:
            # layer = layers[layer_num]
            if layer not in layer_graphs:
                logger.warning("Layer %s not in the graph, cannot display it." % layer)
                continue

            if only_in_layer:

                pos = poss[layer]

            else:
                pos = pos_ml

            layer_gr = layer_graphs[layer]
            # print(layer,len(layer_gr.es))
            if len(layer_gr.es) == 0:
                continue

            if layer not in layer_gr.edge_attributes():
                self.addLayerName()

            for e in layer_gr.es.select(layer=layer):
                if e.source == e.target:
                    continue

                if only_in_layer:
                    es = e.source
                    et = e.target
                else:
                    es = self.multi_layer.vs.find(label=layer_gr.vs[e.source]["label"]).index
                    et = self.multi_layer.vs.find(label=layer_gr.vs[e.target]["label"]).index

                Xe += [pos[es][0], pos[et][0], None]  # x-coordinates of edge ends
                Ye += [pos[es][1], pos[et][1], None]
                # Ze += [layers.index(layer), layers.index(layer),None]
                Ze += [layer, layer, None]
        # texts = ["%s-%s"%(e["year_s"],e["year_e"]) for e in gr.es]

        intralayer_trace = go.Scatter3d(x=Xe,
                                        y=Ye,
                                        z=Ze,
                                        mode='lines',
                                        line=dict(color='rgb(40,20,20)', width=1.5),
                                        # text = texts,
                                        hoverinfo='text'
                                        )

        # generste nodes

        Xn = []
        Yn = []
        Zn = []
        text = []
        scale = []
        for l in range(0, len(layer), 10):  # color will repeat every 10 layers
            scale += colorlover.scales['10']["qual"]["Paired"]

        color = []

        for layer in layers:
            if layer not in layer_graphs:
                logger.warning("Layer %s not in the graph, cannot display it." % layer)
                continue

            if only_in_layer:
                pos = poss[layer]
                gr = self[layer]
            else:
                pos = pos_ml
                gr = self.multi_layer

            Xn += [k[0] for k in pos.coords]  # x-coordinates of nodes
            Yn += [k[1] for k in pos.coords]  # x-coordinates of nodes
            # Zn += [layers.index(layer) for k in self.multi_layer.vs]
            Zn += [layer for k in gr.vs]
            text += gr.vs["label"]
            color += [scale[layers.index(layer)] for x in pos.coords]

        if isinstance(sizes, dict):
            sizes_joined = []
            for layer in layers:
                sizes_joined += sizes[layer]
        else:
            sizes_joined = sizes

        trace_persons = go.Scatter3d(x=Xn,
                                     y=Yn,
                                     z=Zn,
                                     mode='markers',
                                     name='actors',
                                     marker=dict(symbol='circle',
                                                 size=sizes_joined,
                                                 # color=group,
                                                 colorscale='Viridis',
                                                 color=color,
                                                 line=dict(color='rgb(10,10,10)', width=0.5)
                                                 ),
                                     text=text,
                                     hoverinfo='text'
                                     )

        axis = dict(showbackground=False,
                    showline=False,
                    zeroline=True,
                    showgrid=True,
                    showticklabels=False,
                    title=''
                    )

        zaxis = axis.copy()
        zaxis["type"] = "category"
        zaxis["categoryorder"] = "array"
        zaxis["categoryarray"] = layers
        zaxis["showticklabels"] = True

        layout = go.Layout(
            title="",
            width=1000,
            height=1000,
            showlegend=False,
            scene=dict(
                xaxis=dict(axis),
                yaxis=dict(axis),
                zaxis=dict(zaxis),
            ),
            margin=dict(
                t=100
            ),
            hovermode='closest',
            annotations=[
                dict(
                    showarrow=False,
                    text=name,
                    xref='paper',
                    yref='paper',
                    x=0,
                    y=0.1,
                    xanchor='left',
                    yanchor='bottom',
                    font=dict(
                        size=14
                    )
                )
            ], )

        data = [intralayer_trace, trace_persons, interlayer_trace]
        # data=[intralayer_trace,trace2]
        self._multilayer_fig = go.Figure(data=data, layout=layout)

    def unify_attributes(self):
        """
        adds the attributes of every node to every layer, if it exists there, creates also a unified node list.

        :return:
        """
        # first generate all_nodes
        self._all_nodes = defaultdict(dict)

        try:
            for v in self.multi_layer.vs:
                self._all_nodes[(v["label"], v["typ"])].update(v.attributes())
                del self._all_nodes[(v["label"], v["typ"])]["id"]  # id is specific for each graph and shouldn't be here
        except NotCalculatedYetError:
            pass

        for ln,gr in self.items():
            for n in gr.vs:
                for k, v in n.attributes().items():
                    if k == "id":
                        continue  ## id is normally graph specific
                    if v and not v == "None":
                        oldValue = self._all_nodes[(n["label"], n["typ"])].get(k, None)
                        if oldValue == "None":
                            oldValue = None

                        if isinstance(oldValue,float) and math.isnan(oldValue):
                            self._all_nodes[(n["label"], n["typ"])][k] = v
                        elif oldValue and not oldValue == v:
                            try:
                                if float(oldValue) != float(v):  # could just be the same value but different types - in the case of floats or ints
                                    raise ValueError("layer %s not all values %s the same for: %s was (%s)" % (ln, k, n, oldValue))
                            except:
                                raise ValueError("layer %s not all values %s the same for: %s was (%s)" % (ln,k, n, oldValue))
                        else:
                            self._all_nodes[(n["label"], n["typ"])][k] = v

        # now add this values to all graphs
        try:
            for v in self.multi_layer.vs:
                for k, val in self._all_nodes[(v["label"], v["typ"])].items():
                    v[k] = val
        except NotCalculatedYetError:
            pass

        for gr in self.values():
            for v in gr.vs:
                for k, val in self._all_nodes[(v["label"], v["typ"])].items():
                    v[k] = val

    @property
    def ynws(self):
        if self._ynws is None:
            logger.info("multi_layer not calculated yet. Please run createYearNetworks first!")
            raise NotCalculatedYetError("multi_layer not calculated yet. Please run createYearNetworks first!")
        else:
            return self._ynws

    def createYearNetworks(self, start, end,
                           v_attr_name="label",
                           startyear_attr="begins",
                           endyear_attr="ends",
                           startyear_edge_attr="year_s",
                           endyear_edge_attr="year_e",
                           filter_degree_0=False,
                           include_nodes_without_date=False,
                           simplify=False,
                           combine_edges=None,
                           update=False,
                           worker =  6):

        ynws = {}
        for v, gr in self.items():

            # if update:
            #    ynws = self._ynws
            #    if v in ynws:
            #        continue

            if not startyear_attr in gr.vertex_attributes():
                logging.warning("%s not in vertex attributes of graph %s !" % (startyear_attr, v))

            if not endyear_attr in gr.vertex_attributes():
                logging.warning("%s not in vertex attributes of graph %s !" % (endyear_attr, v))

            if not endyear_edge_attr in gr.edge_attributes():
                logging.warning("%s not in edge attributes of graph %s !" % (endyear_edge_attr, v))

            if not startyear_edge_attr in gr.edge_attributes():
                logging.warning("%s not in edge attributes of graph %s !" % (startyear_edge_attr, v))

            logger.debug("%s type %s" % (v, type(gr)))
            ynws[v] = igraphx.createYearNetworksParallel(gr, start, end,
                                                         tqdm=tqdm,
                                                         startyear_attr=startyear_attr,
                                                         endyear_attr=endyear_attr,
                                                         startyear_edge_attr=startyear_edge_attr,
                                                         endyear_edge_attr=endyear_edge_attr,
                                                         filter_degree_0=filter_degree_0,
                                                         include_nodes_without_date=include_nodes_without_date,
                                                         simplify=simplify,
                                                         combine_edges=combine_edges,
                                                         worker = worker)

        if not update:
            self._ynws = MultiLayerGraph.YearNetwork()

        self._ynws.init_params(start,
                               end,
                               startyear_attr,
                               endyear_attr,
                               startyear_edge_attr,
                               endyear_edge_attr
                               )

        for v, ynw in ynws.items():
            for y, gr in ynw.items():
                nw = self._ynws.get(y, MultiLayerGraph())
                nw[v] = gr
                nw.generateMultiLayer(v_attr_name=v_attr_name)
                self._ynws[y] = nw
        return True

    def createFigMultiLayerYearNW(self, name,
                                  layers,
                                  func="betweenness",
                                  size_mult=20,
                                  size_offset=5,
                                  bipartite=False,
                                  years_selected=None,
                                  only_in_layer=False,
                                  disable=True):
        figs = {}

        if logger.getEffectiveLevel() >= logging.DEBUG:
            disable = False
        else:
            disable = disable
        # print(logger.level,logging.DEBUG)
        for y, nw in tqdm(self._ynws.items(), disable=disable):
            if years_selected and not y in years_selected:
                logger.info("skip: %s"%y)
                continue
            sizes = nw.calc_sizes(size_mult=size_mult, size_offset=size_offset, func=func)
            if bipartite:
                logger.debug(("bipartite mode"))
                nw.createFigLayeredGraphBip(name, layers, sizes, only_in_layer=only_in_layer)
            else:
                logger.debug(("non bipartite mode"))
                nw.createFigLayeredGraph(name, layers, sizes, only_in_layer=only_in_layer)
            figs[y] = nw.multilayer_fig
        self._ynws_multilayer_figs = figs

        return True

    @property
    def ynws_multilayer_figs(self):
        if self._ynws_multilayer_figs is None:
            logger.info("ynw_figs not calculated yet. Please run createFigMultiLayerYearNW first!")
            return None
        else:
            return self._ynws_multilayer_figs

    def update_multilayer(self, v_attr_name=None):


        if v_attr_name is None:
            v_attr_name = self._multi_layer_v_attr_name
            if v_attr_name is None:
                logger.info("No v_attr_name given and no multilayer exists. I will create one with the default settings.")
            else:
                logger.info("No v_attr_name given, will use the stored one: %s" % v_attr_name)

        logger.debug("Step1: Adding layer name.")
        self.addLayerName()
        logger.debug("Step2: Generate Multilayer v_attr_name = %s", v_attr_name)

        self.generateMultiLayer(v_attr_name, update=True)

        logger.debug("Step2a: Unify attributes.")

        self.unify_attributes()
        logger.debug("Step3: Update all")
        self.ynws._update_all(self)


        if not self._merged_ynws:
            logger.debug("no merged intervalls yet.")
        else:
            logger.debug("Step4: Merged")
            self.generateMerged_ynws(self.merged_ynws.keys(),
                                     update=True,
                                     chooseOnlyNodesInYear=self.merged_ynws._chooseOnlyNodesInYear,
                                     mergeattr=self.merged_ynws._mergeattr,
                                     start_attr=self.merged_ynws._start_attr_merge,
                                     end_attr=self.merged_ynws._end_attr_merge)

    def ynws_plt(self, y):
        iplot(self.ynws_multilayer_figs[y], validate=False)

    # _merged_intervalls = None

    @property
    def merged_ynws(self):
        if self._merged_ynws is None:
            logger.info("no merged_ynws calculated yet. Please run generateMerged_ynws first!")
            raise NotCalculatedYetError
        else:
            return self._merged_ynws

    def generateMerged_ynws(self, intervalls, update=True,
                            chooseOnlyNodesInYear=False,
                            mergeattr="label",
                            start_attr="begins",
                            end_attr="ends",
                            ):

        if intervalls is None:
            logger.info("intervall is None, won't do anything!")
            return  # nothing to be done

        if self._merged_ynws is None:
            self._merged_ynws = MultiLayerGraph.MergedYearNetwork(chooseOnlyNodesInYear, mergeattr, start_attr,
                                                                  end_attr)
            # self._merged_ynws.init_params(chooseOnlyNodesInYear,mergeattr,start_attr,end_attr)

        else:
            logger.debug("ynw already existing.")
            if update:
                logger.info("update is true, I will ignore all further params of this call and use the stored one!")
            else:
                logger.debug("update is false. I recreate everything.")
                self._merged_ynws = MultiLayerGraph.MergedYearNetwork()
                self._merged_ynws.init_params(chooseOnlyNodesInYear, mergeattr, start_attr, end_attr)

        if not self._ynws:
            logger.info("I am creating the the ynws first")

        for i in intervalls:
            if i in self._merged_ynws and update:
                continue

            mg = MultiLayerGraph.YearNetwork()
            for layer in self.keys():
                ynw_layer = self.getLayerYNW(layer)
                ynw_layer_merged = igraphx.mergeAllGraphsIntervall(ynw_layer,
                                                                   i,
                                                                   chooseOnlyNodesInYear=chooseOnlyNodesInYear,
                                                                   mergeattr=mergeattr,
                                                                   start_attr=start_attr,
                                                                   end_attr=end_attr)
                for y in self._ynws.keys():
                    mg[y][layer] = ynw_layer_merged[y]

            for y in self._ynws.keys():
                mg[y].generateMultiLayer(self._multi_layer_v_attr_name)

            intervall_mg = MultiLayerGraph()
            intervall_mg._multi_layer = self.multi_layer  # is the same as of the parent
            intervall_mg._ynws = mg
            intervall_mg._intervall = i
            self._merged_ynws[i] = intervall_mg

    def getLayerYNW(self, layer):
        """
        Create ther ynw for a layer
        :param layer: layername
        :return: dict year -> nw.
        """

        ynw = {}
        for y, gr in self.ynws.items():
            ynw[y] = gr[layer]

        return ynw

    def createFigLayeredGraphBip(self, name, layers, sizes, only_in_layer=False, scale_positions=True, layer_typ={}, nolines = False):

        layer_graphs = self
        pos_ml = self.multi_layer.layout_fruchterman_reingold()

        poss = {}
        if only_in_layer:
            for l, gr in self.items():
                poss[l] = gr.layout_fruchterman_reingold()

            if scale_positions:
                poss_neu = {}
                max_x = 0
                max_y = 0

                for k, p in poss.items():
                    try:
                        max_x = max(max([x[0] for x in p]), max_x)
                    except ValueError:
                        logging.error("no nodes in %s (X)"%k)
                        return

                    try:
                        max_y = max(max([x[1] for x in p]), max_y)
                    except ValueError:
                        logging.error("no nodes in %s (Y)" % k)
                        return

                for k, p in poss.items():
                    xs = [x[0] for x in p]
                    ys = [x[1] for x in p]

                    xs = np.array(xs) / max(xs) * max_x
                    ys = np.array(ys) / max(ys) * max_y

                    poss_neu[k] = list(zip(xs, ys))
                poss = poss_neu
            else:
                poss_neu = {}
                for k, p in poss.items():
                    xs = [x[0] for x in p]
                    ys = [x[1] for x in p]

                    xs = np.array(xs)
                    ys = np.array(ys)

                    poss_neu[k] = list(zip(xs, ys))
                poss = poss_neu

        # layers = [l for l in layers_all if not isinstance(l, MultiLayerGraph.BiPartiteGraph)]

        # generate links between the layers

        Xl = []
        Yl = []
        Zl = []

        for layer_num in range(0, len(layers) - 1):
            layer = layers[layer_num]
            layer_gr = layer_graphs[layer]

            # choose iteration
            if only_in_layer:
                iteration = layer_gr.vs
            else:
                iteration = self.multi_layer.vs

            if isinstance(layer_gr, MultiLayerGraph.BiPartiteGraph):
                iteration = layer_gr.es
                assert layer_gr._layer_start is not None, "You have to setStartLayer for layer: %s" % layer
                assert layer_gr._layer_end is not None, "You have to setEndLayer for layer: %s" % layer

                source_layer = layer_graphs[layer_gr._layer_start]
                target_layer = layer_graphs[layer_gr._layer_end]
                source_layer_name = layer_gr._layer_start
                target_layer_name = layer_gr._layer_end

            else:
                source_layer = layer_gr
                source_layer_name = layer

                target_layer_name = layers[layer_num + 1]
                target_layer = layer_graphs[target_layer_name]
                if isinstance(target_layer, MultiLayerGraph.BiPartiteGraph):  # no link to bipartite
                    continue

            logger.debug("Made the folloing settings for layer: %s" % layer)
            logger.debug("source layer: %s" % source_layer_name)
            logger.debug("target layer: %s" % target_layer_name)

            if only_in_layer:
                pos_s = poss[source_layer_name]
                pos_t = poss[target_layer_name]

            else:
                pos_s = pos_ml
                pos_t = pos_ml

            for n in iteration:
                ni = None

                if isinstance(n, igraph.Vertex):
                    ni = n.index
                else:
                    # ni = n.target

                    for check_n in [n.source, n.target]:
                        try:
                            if only_in_layer:
                                ni = source_layer.vs.find(label=layer_gr.vs[check_n]["label"]).index
                            else:
                                source_layer.vs.find(label=layer_gr.vs[check_n][
                                    "label"]).index  ##nachschauen ob in source netzwerk - ergebnis aber ignorieren
                                ni = self.multi_layer.vs.find(label=layer_gr.vs[check_n]["label"]).index
                            break  # in dem layer, dann fertig
                        except ValueError:
                            # nicht dem layer
                            continue

                    if not ni:  # ist nicht im verbundene Layer
                        continue
                x = pos_s[ni][0]
                y = pos_s[ni][1]
                # z = layers.index(layer)
                z = source_layer_name

                # layer = layers[layer_num + 1]
                # layer_gr = layer_graphs[layer]

                # if only_in_layer:
                #     try:
                #         n_tmp = target_layer.vs.find(label=label)  # TODO search also for typ
                #         ni = n_tmp.index
                #     except:
                #         continue
                # else:
                #     ni = n.index

                ni = None
                if isinstance(n, igraph.Vertex):

                    if only_in_layer:
                        try:
                            ni = target_layer.vs.find(label=n["label"]).index
                        except ValueError:  # not in target
                            continue  # no link
                    else:
                        ni = n.index

                else:
                    for check_n in [n.source, n.target]:
                        try:
                            if only_in_layer:
                                ni = target_layer.vs.find(label=layer_gr.vs[check_n]["label"]).index
                            else:
                                target_layer.vs.find(label=layer_gr.vs[check_n][
                                    "label"]).index  ##nachschauen ob in target netzwerk - ergebnis aber ignorieren
                                ni = self.multi_layer.vs.find(label=layer_gr.vs[check_n]["label"]).index
                            break
                        except ValueError:
                            continue

                    if not ni:  # ist nicht im verbundenen Layer
                        continue

                x1 = pos_t[ni][0]
                y1 = pos_t[ni][1]
                # z1 = layers.index(layer)
                z1 = target_layer_name

                Xl += [x, x1, None]
                Yl += [y, y1, None]
                Zl += [z, z1, None]

        trace3 = go.Scatter3d(x=Xl,
                              y=Yl,
                              z=Zl,
                              mode='lines',
                              line=dict(color='rgb(50,20,20)', width=0.2),
                              # text = texts,
                              hoverinfo='text'
                              )

        # print(len (Xl),len(Yl),len(Zl))

        # generate lines in the layers

        Xe = []
        Ye = []
        Ze = []
        for layer in layers:
            try:
                layer_gr = layer_graphs[layer]
            except KeyError:
                logger.warning("Layer %s not in the graph, cannot display it." %layer_gr)
                continue
            if isinstance(layer_gr, MultiLayerGraph.BiPartiteGraph):
                continue

            # layer = layers[layer_num]

            if only_in_layer:
                pos = poss[layer]

            else:
                pos = pos_ml

            # print(layer,len(layer_gr.es))
            if len(layer_gr.es) == 0:
                continue

            if layer not in layer_gr.edge_attributes():
                self.addLayerName()

            for e in layer_gr.es.select(layer=layer):
                if e.source == e.target:
                    continue

                if only_in_layer:
                    es = e.source
                    et = e.target
                else:
                    es = self.multi_layer.vs.find(label=layer_gr.vs[e.source]["label"]).index
                    et = self.multi_layer.vs.find(label=layer_gr.vs[e.target]["label"]).index

                Xe += [pos[es][0], pos[et][0], None]  # x-coordinates of edge ends
                Ye += [pos[es][1], pos[et][1], None]
                # Ze += [layers.index(layer), layers.index(layer),None]
                Ze += [layer, layer, None]
        # texts = ["%s-%s"%(e["year_s"],e["year_e"]) for e in gr.es]

        trace1 = go.Scatter3d(x=Xe,
                              y=Ye,
                              z=Ze,
                              mode='lines',
                              line=dict(color='rgb(40,20,20)', width=1.5),
                              # text = texts,
                              hoverinfo='text'
                              )

        # generste nodes

        Xn = []
        Yn = []
        Zn = []
        text = []
        scale = []
        for l in range(0, len(layer), 10):  # color will repeat every 10 layers
            scale += colorlover.scales['10']["qual"]["Paired"]

        color = []

        for layer in layers:
            layer_gr = layer_graphs[layer]
            if isinstance(layer_gr, MultiLayerGraph.BiPartiteGraph):
                continue

            if only_in_layer:
                pos = poss[layer]
                gr = self[layer]
            else:
                pos = pos_ml
                gr = self.multi_layer

            # label = n["label"]
            pos_tmp = []
            text_temp = []
            if layer_typ and "typ" in gr.vertex_attributes():
                for n in gr.vs:
                    # print(layer,n["typ"],layer_typ[layer])
                    if not n["typ"] in layer_typ[layer]:
                        continue
                    pos_tmp.append(pos[n.index])
                    text_temp.append(n["label"])
            else:
                pos_tmp = pos
                text_temp = gr.vs["label"]

            Xn += [k[0] for k in pos_tmp]  # x-coordinates of nodes
            Yn += [k[1] for k in pos_tmp]  # x-coordinates of nodes
            # Zn += [layers.index(layer) for k in self.multi_layer.vs]
            Zn += [layer for k in pos_tmp]
            # text += gr.vs["label"]
            text += text_temp
            color += [scale[layers.index(layer)] for x in pos_tmp]

        if isinstance(sizes, dict):
            sizes_joined = []
            for layer in layers:
                sizes_joined += sizes[layer]
        else:
            sizes_joined = sizes

        trace_persons = go.Scatter3d(x=Xn,
                                     y=Yn,
                                     z=Zn,
                                     mode='markers',
                                     name='actors',
                                     marker=dict(symbol='circle',
                                                 size=sizes_joined,
                                                 # color=group,
                                                 colorscale='Viridis',
                                                 color=color,
                                                 line=dict(color='rgb(10,10,10)', width=0.5)
                                                 ),
                                     text=text,
                                     hoverinfo='text'
                                     )

        axis = dict(showbackground=False,
                    showline=False,
                    zeroline=True,
                    showgrid=True,
                    showticklabels=False,
                    title=''
                    )

        zaxis = axis.copy()
        zaxis["type"] = "category"
        zaxis["categoryorder"] = "array"
        zaxis["categoryarray"] = layers
        zaxis["showticklabels"] = True

        layout = go.Layout(
            title="",
            width=1000,
            height=1000,
            showlegend=False,
            scene=dict(
                xaxis=dict(axis),
                yaxis=dict(axis),
                zaxis=dict(zaxis),
            ),
            margin=dict(
                t=100
            ),
            hovermode='closest',
            annotations=[
                dict(
                    showarrow=False,
                    text=name,
                    xref='paper',
                    yref='paper',
                    x=0,
                    y=0.1,
                    xanchor='left',
                    yanchor='bottom',
                    font=dict(
                        size=14
                    )
                )
            ], )

        if nolines:
            data = [trace1, trace_persons]
        else:
            data = [trace1, trace_persons, trace3]
        # data=[trace3]
        self._multilayer_fig = go.Figure(data=data, layout=layout)

    def info(self, deep=False):
        print("Multilayergraph")
        print("===============")

        print("\nLayer: ")
        print("--------")
        for k, gr in self.items():
            print(k, type(gr))

        print("\nMultilayer")
        print("-----------")
        try:
            print("Nodes: %s" % len(self.multi_layer.vs))
            print("Edges: %s" % len(self.multi_layer.es))
            print("Components added: %s" % self.multi_layer._components)
        except NotCalculatedYetError:
            print("NOT calculated yet!")

        print("\nYear networks")
        print("--------")
        try:
            print("years: %s" % list(self.ynws.keys()))
            for its in self.ynws.__dict__.items():
                print("%s : %s" % its)
            for y, ml in self.ynws.items():
                print("     %s: %s" % (y, list(ml.keys())))

        except NotCalculatedYetError:
            print("NOT calculated yet!")

        print("\nYear merged networks")
        print("--------")

        try:
            print("Intervalls: %s" % list(self.merged_ynws.keys()))
            print("  ChooseOnlyNodesInYear: %s" % self.merged_ynws._chooseOnlyNodesInYear)
            print("  Mergeattr: %s" % self.merged_ynws._mergeattr)
            print("  Start attr: %s" % self.merged_ynws._start_attr_merge)
            print("  End attr: %s" % self.merged_ynws._end_attr_merge)

            if deep and self.merged_ynws:
                print("intervalls: %s" % list(self.merged_ynws.keys()))
                for i, k in self.merged_ynws.items():
                    print("--------------------------------")
                    print("_____________ %s _______________" % i)
                    k.info()
                    print("--------------------------------")

        except NotCalculatedYetError:
            print("NOT calculated yet!")

    def biPartiteToAttribute(self, bip2attr=None):
        """
        Create attributes out of bipartite networks it will always at the attributes to the end layer, therefore it assumes that _layer_end is set
        for each of the bipartite networks (with setEndLayer)!

        :param bip2attr: (optional) dict -> bi-parite layer name to attribute name
        :return:
        """
        if not bip2attr:
            bip2attr = {k: k for k in self.keys()}

        logger.debug("FIRST: the layer")
        for v, k in self.items():
            if isinstance(k, MultiLayerGraph.BiPartiteGraph):
                k.biPartiteToAttribute(bip2attr[v], self[k._layer_end])

        self.generateMultiLayer(v_attr_name=self._multi_layer_v_attr_name)

        logger.debug("SECOND: the layer of the year networks")
        for ynw in self.ynws.values():
            for v, k in ynw.items():
                if isinstance(k, MultiLayerGraph.BiPartiteGraph):
                    k.biPartiteToAttribute(bip2attr[v], ynw[k._layer_end])
            ynw.generateMultiLayer(v_attr_name=self._multi_layer_v_attr_name)

        logger.debug("THIRD: the layer of the merged year networks")
        for merged_ynws in self.merged_ynws.values():
            for ynw in merged_ynws.ynws.values():
                for v, k in ynw.items():
                    # layer_end  = self[v].__layer_end
                    if isinstance(k, MultiLayerGraph.BiPartiteGraph):
                        layer_end = self[v]._layer_end
                        k.biPartiteToAttribute(bip2attr[v], ynw[layer_end])
                ynw.generateMultiLayer(v_attr_name=self._multi_layer_v_attr_name)

    def writeGraphsToFile(self, fl, outputTypes=["graphml"]):
        """
        :param fl: filehandle
        :param outputTypes: list of output types defaults to ["graphml"]
        :return:
        """

        tf = tarfile.open(fileobj=fl, mode="w:gz")

        for outputType in outputTypes:

            # first the multilayer
            temp = tempfile.NamedTemporaryFile(delete=False)
            self.multi_layer.write(temp.name, outputType)

            tf.add(temp.name, arcname="multi/all.%s" % outputType)
            os.unlink(temp.name)

            # now each layer
            for v, k in self.items():
                temp = tempfile.NamedTemporaryFile(delete=False)
                k.write(temp.name, outputType)
                tf.add(temp.name, arcname="multi/layer_%s.%s" % (v, outputType))
                os.unlink(temp.name)

            # now the layers of each year network

            for y, ynw in self.ynws.items():

                temp = tempfile.NamedTemporaryFile(delete=False)
                ynw.multi_layer.write(temp.name, outputType)

                tf.add(temp.name, arcname="multi/%s.%s" % (y, outputType))
                os.unlink(temp.name)

                for v, k in ynw.items():
                    temp = tempfile.NamedTemporaryFile(delete=False)
                    k.write(temp.name, outputType)
                    tf.add(temp.name, arcname="multi/%s/%s.%s" % (v, y, outputType))
                    os.unlink(temp.name)

            # merged_networks

            for intervall, merged_ynws in self.merged_ynws.items():
                for y, ynw in merged_ynws.ynws.items():
                    temp = tempfile.NamedTemporaryFile(delete=False)
                    ynw.multi_layer.write(temp.name, outputType)

                    tf.add(temp.name, arcname="multi/intervall_%s/%s.%s" % (intervall, y, outputType))
                    os.unlink(temp.name)

                    for v, k in ynw.items():
                        temp = tempfile.NamedTemporaryFile(delete=False)
                        k.write(temp.name, outputType)
                        tf.add(temp.name, arcname="multi/intervall_%s/%s/%s.%s" % (intervall, v, y, outputType))
                        os.unlink(temp.name)

        tf.close()

    def createSubNetwork(self, layers):
        """
        Create a subnetwork consisting from the muli-layer with the layers given.
        :param layers: list of layer names in the new network
        :return:
        """

        for l in layers:
            if not l in self:
                logger.warning("%s not in %s." % (l, list(self.keys())))
                logger.warning("Will be ignored!")
        nw = self.copy()

        logger.debug("FIRST: the layer")
        for v in list(nw):
            if not v in layers:
                del nw[v]

        nw.generateMultiLayer(v_attr_name=self._multi_layer_v_attr_name)
        nw.createFigGraph()
        logger.debug("SECOND: the layer of the year networks")
        for ynw in nw.ynws.values():
            for v in list(ynw):
                if not v in layers:
                    del ynw[v]
            ynw.generateMultiLayer(v_attr_name=self._multi_layer_v_attr_name)

        logger.debug("THIRD: the layer of the merged year networks")
        for merged_ynws in nw.merged_ynws.values():
            for ynw in merged_ynws.ynws.values():
                for v in list(ynw):
                    if not v in layers:
                        del ynw[v]
                ynw.generateMultiLayer(v_attr_name=self._multi_layer_v_attr_name)

        return nw

    def copy(self):
        nw = super().copy()

        nw._merged_ynws = {}
        try:
            for v, w in self.merged_ynws.items():
                nw._merged_ynws[v] = w.copy()
        except NotCalculatedYetError:
            pass  # if  not calculated in source ignore

        nw._ynws = self.ynws.copy()
        return nw

    def checkValidity(self):
        """For a number of functions - a specific set of attributes is expected, check if the multilayer graph full fills this."""

        # first check for label attribute

        print("Check 'label' attribute for vertices in all layers:")
        correct = True
        for n, gr in self.items():

            if not "label" in gr.vertex_attributes():
                print("FATAL: %s no 'label'!" % n)
                correct = False

        if not correct:
            print("-------FAILED")
        else:
            print("-------OK")

        print("Check begins/ends for vertices (necessary for year graphs)!")
        correct = True

        for n, gr in self.items():

            if not "begins" in gr.vertex_attributes():
                print("WARNING: %s no 'begins'!" % n)
                correct = False

            if not "ends" in gr.vertex_attributes():
                print("WARNING: %s no 'ends'!" % n)
                correct = False

        if not correct:
            print("-------WARNING")
        else:
            print("-------OK")

        print("Check year_s/year_e for edges (optional for year graphs)!")
        correct = True

        for n, gr in self.items():

            if not "year_s" in gr.edge_attributes():
                print("INFO: %s not year_s!" % n)
                correct = False

            if not "year_e" in gr.edge_attributes():
                print("INFO: %s not 'year_e!" % n)
                correct = False

        if not correct:
            print("-------INFO")
        else:
            print("-------OK")

        print("check startLayer / endLayer")
        correct = True
        for n, gr in self.items():
            if isinstance(gr, MultiLayerGraph.BiPartiteGraph):
                try:
                    x = gr.startLayer
                    if not x in self:
                        print("ERROR: startLayer %s of %s not in MultiLayerGraph!" % (n, x))
                        correct = False
                except:
                    print("INFO: %s no start_layer!" % n)
                    correct = False
                try:
                    x = gr.endLayer
                    if not x in self:
                        print("ERROR: endLayer %s of %s not in MultiLayerGraph!" % (n, x))
                        correct = False
                except:
                    print("INFO: %s no end_layer!" % n)
                    correct = False
        if not correct:
            print("-------INFO")
        else:
            print("-------OK")

    def get_simplified_multi_layer_ynws(self, intervall: int):
        """simplifies the multi layer  year network for the intervall"

        :type intervall: int
        :param intervall: Intervall has to be 1 or an intervall contained in the merged networks
        :returns yearnetworks: dict with different type of simplified networks
        """

        ynws_lc_tmp = defaultdict(MultiLayerGraph.YearNetwork)

        if intervall == 1:
            ynw = self.ynws

        elif intervall in self.merged_ynws:
            ynw = self.merged_ynws[intervall].ynws
        else:
            raise  KeyError("%s not in merged_ynws!"%intervall)

        for y, gr_tmp in ynw.items():
            gr = gr_tmp.multi_layer
            ynws_lc_tmp["original"][y] = gr
            ynws_lc_tmp["undirected"][y] = to_undirected(gr)
            ynws_lc_tmp["loop_free"][y] = gr.simplify(multiple=False, loops=True)
            ynws_lc_tmp["loop_free_undirected"][y] = ynws_lc_tmp["undirected"][y].simplify(multiple=False, loops=True)
            ynws_lc_tmp["simplified"][y] = gr.simplify()
            ynws_lc_tmp["simplified_undirected"][y] = ynws_lc_tmp["undirected"][y].simplify()

        return ynws_lc_tmp

    def simulate(self, onlyMultilayer=True, intervall=-100, iterations=2):
        """this method takes a merged year network and creates - simular graphs with Erdos_Renyi and Barabasi
           and returns yeargraphs for both cases and the development of some graph properties
           (no of nodes and no of edges)

           We generate simulations for different versions of the original set of graphs.
           If the graph contains loops simulation of the
           original graph will not get usefull results. Therefore it is recommended to use at least the loop-free simulation.

           This methods calls :py:func:`simulate_ynw` for each layer

           :param onlyMultilayer: defaults to True. Only the multi layer graph for each year is simulated
           :param intervall: defaults to -100. Uses the merged_graph for -100 as basis for simulation
           :param iterations: defaults to 2. Number of  simulations should be done for each year.

           :return: dict with layer -> simuation, each simulation is a results of  :py:func:`simulate_ynw`.
           """
        mls = {}

        for k, v in self.merged_ynws[intervall].ynws.items():
            mls[k] = v.multi_layer

        ynws_dict = {"multilayer": mls}

        if not onlyMultilayer:
            for k in list(self.keys()):
                ynws_dict[k] = {y: x[k] for y, x in self.merged_ynws[intervall].ynws.items()}
        logger.debug("Simulate")

        simulation = {k: self.simulate_ynw(n, iterations=iterations) for k, n in ynws_dict.items()}
        return simulation

    def simulate_ynw(self, ynw, iterations=2):
        """
        Simulate for each year different versions of the networks. Normally, you should at least use the loop free versions.

        In the output you find information for:

        * "graphs" :  the graph as it is
        * "undirected" : undirected version of the graph using as_undirected() from igraph
        * "loop_free" : remove all loops
        * "loop_free_undirected" : no loops and undirected
        * "simplify" : calls simplify() on all graps
        * "simplify_undirected" : simplify and undirected

        :param ynw: :py:class:`YearNetwork`
        :param iterations: optional defaults to 2, number of iterations for each simluation

        :return: :ref:`structure_simulations`
        """
        # res = {t: defaultdict(pandas.DataFrame) for t in ["graphs", "largest_component"]}
        ynws_lc_tmp = {}

        for y, gr in ynw.items():
            undir = to_undirected(gr)
            ynws_lc_tmp[y] = {"graphs": gr,
                              # "largest_component": gr.components(mode=igraph.WEAK).giant(),
                              "undirected": undir,
                              "loop_free": gr.simplify(multiple=False, loops=True),
                              "loop_free_undirected": undir.simplify(multiple=False, loops=True),
                              # "largest_component_undirected": gr.as_undirected().components(mode=igraph.WEAK).giant(),
                              "simplified": gr.simplify(),
                              "simplified_undirected": undir.simplify(),
                              }

        ynws_lc = defaultdict(dict)
        for y, graph_type_gr in ynws_lc_tmp.items():
            for graph_type, graph in graph_type_gr.items():
                ynws_lc[graph_type][y] = graph

        graph_types = ynws_lc.keys()

        # now we simulate
        sims = {}
        for graph_type in graph_types:
            sims[graph_type] = simulations.simulate_largest_components(ynws_lc[graph_type], iterations=iterations)

        # create the graphproperies structure -> graph_type -> sim_type -> value -> year
        graphproperties = defaultdict()
        for graph_type in graph_types:
            sim_method_properties = {}
            for sim_method in ["original"] + SIM_METHODS:
                sim_method_properties[sim_method] = pandas.DataFrame(index=ynw.keys())
                # add some values for each graph
                if sim_method == "original":
                    for v in ["graph_no_nodes", "graph_no_edges", "largest_component_no_nodes",
                              "largest_component_no_edges"]:
                        sim_method_properties[sim_method][v] = pandas.Series(index=ynw.keys())

            for y, graph in ynws_lc[graph_type].items():
                # graph = graphs[graph_type]
                lc = graph.components(mode=igraph.WEAK).giant()
                sim_method_properties["original"]["graph_no_nodes"][y] = len(graph.vs)
                sim_method_properties["original"]["graph_no_edges"][y] = len(graph.es)

                sim_method_properties["original"]["largest_component_no_nodes"][y] = len(lc.es)
                sim_method_properties["original"]["largest_component_no_edges"][y] = len(lc.es)

            graphproperties[graph_type] = sim_method_properties

        simulations.addProperty(graphproperties, "density", ynws_lc, simulations=sims)
        simulations.addProperty(graphproperties, "no_nodes", ynws_lc, simulations=sims, reset=True)
        simulations.addProperty(graphproperties, "no_edges", ynws_lc, simulations=sims, reset=True)
        # simulations.addPropertyMean(sim, "density")

        simulations.addProperty(graphproperties, "average_path_length", ynws_lc, True, simulations=sims)
        # simulations.addPropertyMean(sim, "average_path_length", params=True)

        simulations.addProperty(graphproperties, "radius", ynws_lc, simulations=sims,
                                params=igraph.ALL)
        # simulations.addPropertyMean(sim, "radius", params=igraph.ALL)

        simulations.addProperty(graphproperties, "transitivity_undirected",
                                ynws_lc,
                                simulations=sims)

        return (sims, ynws_lc), graphproperties

    def filter_es(self, *args, **kwds):
        """filter all nodes given bei args,kwargs, parameters are the same as in igraph.es.select
        (#TODO still experimental !!)
        :param args: same as for igraph.vs.select
        :param kwds: same as for igraph.vs.select

        :return: MultiLayerGraph without the selected nodes.
        """

        return self._filter("edge", *args, **kwds)

    def filter_vs(self, *args, **kwds):
        """filter all nodes given bei args,kwargs, parameters are the same as in igraph.es.select
        (#TODO still experimental !!)
        :param args: same as for igraph.vs.select
        :param kwds: same as for igraph.vs.select

        :return: MultiLayerGraph without the selected nodes.
        """
        return self._filter("vertex", *args, **kwds)

    def _filter(self,vertex_or_edge,*args, **kwds):
        """filter all nodes given bei args,kwargs, parameters are the same as in igraph.vs.select
        (#TODO still experimental !!)
        :param args: same as for igraph.vs.select
        :param kwds: same as for igraph.vs.select

        :return: MultiLayerGraph without the selected nodes.
        """
        nw = super().copy()

        # now the layers of each year network
        logger.debug("Step 1: ynws")

        nw._ynws = self._ynws._filter(vertex_or_edge,*args, **kwds)
        # nw._ynws = self._ynws.copy()
        # for y, ynw in nw._ynws.items():
        #
        #     if transform:
        #         transform(ynw.multi_layer,transform)
        #
        #     nds = ynw.multi_layer.vs.select(*args, **kwds)
        #     nds.delete()
        #     for v, k in ynw.items():
        #
        #         if transform:
        #            transform(k,transform)
        #         nds = k.vs.select(*args, **kwds)
        #         nds.delete()

        # merged_networks
        if "transform" in kwds:
            transform_func = kwds["transform"]
            del  kwds["transform"]

        else:
            transform_func = None


        logger.debug("Step 2: layer")

        for v, k in nw.items():

            if transform_func:
                transform(k,transform_func,vertex_or_edge = vertex_or_edge)

            if vertex_or_edge == "vertex":
                nds = k.vs.select(*args, **kwds)
            else:
                nds = k.es.select(*args, **kwds)
            nds.delete()

        logger.debug("Step 3: merged_ynws")
        nw._merged_ynws = {}
        try:
            for v, w in self.merged_ynws.items():
                nw._merged_ynws[v] = w.copy()

            for intervall, merged_ynws in nw._merged_ynws.items():
                for y, ynw in merged_ynws.ynws.items():
                    if transform_func:
                        transform(ynw.multi_layer,transform_func,vertex_or_edge = vertex_or_edge)

                    if vertex_or_edge == "vertex":
                        nds = ynw.multi_layer.vs.select(*args, **kwds)
                    else:
                        nds = ynw.multi_layer.es.select(*args, **kwds)
                    #if len(nds) > 0:
                    #    print("del %s %s"%(y,intervall))
                    nds.delete()

                    for v, k in ynw.items():
                        try:
                            if transform_func:
                               transform(k,transform_func,vertex_or_edge=vertex_or_edge)
                            if vertex_or_edge == "vertex":
                                nds = k.vs.select(*args, **kwds)
                            else:
                                nds = k.es.select(*args, **kwds)
                            nds.delete()
                        except:
                            e = sys.exc_info()
                            logger.debug(e[0], e[1], e[2])
                            logger.warning("""Something (%s) went wrong in year %s. 
                                                       Most likely one of the attributes doesn't exit in this year.""" % (e[0], y))

                        #if len(nds) > 0:
                        #    print("%s %s %s del"% (v,y,intervall))
        except NotCalculatedYetError:
            pass  # if  not calculated in source ignore


        nw.generateMultiLayer(v_attr_name=self._multi_layer_v_attr_name)

        return nw

    def filter_edge_by_vertices(self,start_vertex,end_vertex):
        """filter all nodes given bei args,kwargs, parameters are the same as in igraph.vs.select
        (#TODO still experimental !!)

        :return: MultiLayerGraph without the selected edges.
        """
        nw = super().copy()
        if isinstance(start_vertex, str):
            start_vertex = {"label": start_vertex}
        if isinstance(end_vertex, str):
            end_vertex = {"label": end_vertex}
        # now the layers of each year network
        logger.debug("Step 1: ynws")

        nw._ynws = self._ynws.filter_edge_by_vertices(start_vertex,end_vertex)
        # nw._ynws = self._ynws.copy()
        # for y, ynw in nw._ynws.items():
        #
        #     if transform:
        #         transform(ynw.multi_layer,transform)
        #
        #     nds = ynw.multi_layer.vs.select(*args, **kwds)
        #     nds.delete()
        #     for v, k in ynw.items():
        #
        #         if transform:
        #            transform(k,transform)
        #         nds = k.vs.select(*args, **kwds)
        #         nds.delete()

        # merged_networks

        logger.debug("Step 2: layer")

        for v, k in nw.items():

            s_vs = k.vs.select(**start_vertex)
            e_vs = k.vs.select(**end_vertex)

            for s, e in product(s_vs, e_vs):
                nds=k.es.select(_source=s.index, _target=e.index)
                nds.delete()

        logger.debug("Step 3: merged_ynws")
        nw._merged_ynws = {}
        try:
            for v, w in self.merged_ynws.items():
                nw._merged_ynws[v] = w.copy()

            for intervall, merged_ynws in nw._merged_ynws.items():
                for y, ynw in merged_ynws.ynws.items():

                    s_vs = ynw.multi_layer.vs.select(**start_vertex)
                    e_vs = ynw.multi_layer.vs.select(**end_vertex)

                    for s, e in product(s_vs, e_vs):
                        nds = ynw.multi_layer.es.select(_source=s.index, _target=e.index)
                        nds.delete()

                    for v, k in ynw.items():
                        try:
                            s_vs = k.vs.select(**start_vertex)
                            e_vs = k.vs.select(**end_vertex)

                            for s, e in product(s_vs, e_vs):
                                nds = k.es.select(_source=s.index, _target=e.index)
                                nds.delete()
                        except:
                            e = sys.exc_info()
                            logger.debug(e[0], e[1], e[2])
                            logger.warning("""Something (%s) went wrong in year %s. 
                                                       Most likely one of the attributes doesn't exit in this year.""" % (e[0], y))

                        #if len(nds) > 0:
                        #    print("%s %s %s del"% (v,y,intervall))
        except NotCalculatedYetError:
            pass  # if  not calculated in source ignore


        nw.generateMultiLayer(v_attr_name=self._multi_layer_v_attr_name)

        return nw


def indicators(self, intervall=-100):
    mls = {}
    for k, v in self.ynws.ynws.items():
        mls[k] = v.multi_layer

    ynws_dict = {"all": mls}

    for k in list(self.keys()):
        ynws_dict[k] = {y: x[k] for y, x in self.merged_ynws[intervall].ynws.items()}

    indicators = {k: calculateIndicators(n) for k, n in ynws_dict.items()}

    return indicators


def calculateIndicators(ynw):
    indicators = pandas.DataFrame(columns=ynw.keys(), index=[
        "nodes",
        "edges",
        "average_path_length",
        "average_degree",
        "clustering coefficent",
        "nodes_giant",
        "edges_giant",
        "average_path_length_giant",
        "clustering coefficent_giant",
        "radius_giant",
        "nodes_per",
        "edges_per"
    ])

    # indicators = indicators.transpose()
    for y, gr in ynw.items():
        gr.to_undirected(mode="each")
        gr = gr.simplify(multiple=False)
        number_nodes = len(gr.vs)
        if number_nodes == 0:
            continue
        if len(gr.es) == 0:
            continue
        giant = gr.clusters().giant()

        indicators[y]["nodes"] = len(gr.vs)
        indicators[y]["edges"] = len(gr.es)
        indicators[y]["average_path_length"] = gr.average_path_length()
        indicators[y]["average_degree"] = igraph.mean(gr.degree())
        indicators[y]["clustering coefficent"] = gr.transitivity_undirected()
        indicators[y]["nodes_giant"] = len(giant.vs)
        indicators[y]["edges_giant"] = len(giant.es)
        indicators[y]["average_path_length_giant"] = giant.average_path_length()
        # indicators[y]["clustering coefficent_giant"] = giant.transitivity_undirected()
        indicators[y]["radius_giant"] = giant.diameter()

        # indicators[y]["nodes_per"] =  indicators[y]["nodes_giant"]/indicators[y]["nodes"]
        # indicators[y]["edges_per"] =  indicators[y]["edges_giant"]/indicators[y]["edges"]
    indicators = indicators.transpose()
    indicators["nodes_per"] = indicators["nodes_giant"] / indicators["nodes"]
    indicators["edges_per"] = indicators["edges_giant"] / indicators["edges"]
    return indicators


def saveSimGraphs(sims, fl):
    """
    Saves the output of a simulation to a tar file with relevant networks.
    Including the original.

    :param sims: Should be the output of :py:meth:`network_extensions.igraphx.multilayer.MultiLayerGraph.simulate`
    :param fl: File handle where to write the output to.
    :return:
    """
    tf = tarfile.open(fileobj=fl, mode="w:gz")
    for layer, sims_out in sims.items():
        sim_graphs, ynws_lc = sims_out[0]
        for graph_type, gr_sim in sim_graphs.items():
            for sim, gr_it in gr_sim.items():
                for it, gr_sim_graph_type in gr_it.items():
                    for sim_graph_type, gr_y in gr_sim_graph_type.items():
                        for y, gr in gr_y.items():
                            temp = tempfile.NamedTemporaryFile(delete=False)
                            gr.write(temp, "graphml")
                            tf.add(temp.name, arcname="%s/simulations/%s/%s/%s/%s/%s.graphml" % (
                                layer, graph_type, sim, it, sim_graph_type, y))
                            os.unlink(temp.name)

        for graph_type, gr_y in ynws_lc.items():
            for y, gr in gr_y.items():
                temp = tempfile.NamedTemporaryFile(delete=False)
                gr.write(temp, "graphml")
                tf.add(temp.name, arcname="%s/original/%s/%s.graphml" % (layer, graph_type, y))
                os.unlink(temp.name)

    tf.close()

def to_undirected(gr):
    gr_new = igraph.Graph(directed=False)
    for n in gr.vs:
        gr_new.add_vertex(**n.attributes())

    for e in gr.es:
        gr_new.add_edge(e.source,e.target, **e.attributes())

    return gr_new


def transform(gr, transform,vertex_or_edge = "vertex"):
    """transformes values and creates new for a graph

    :param transform: iterable of dict. Each tripel contains "name" name of vertex attribute to be transformed,
    "func" a callable which can be called with the values of "name". "default" a value which should be used if the
    function call doesn't work. (e.g. {"name" : year, "func" : int, "default": 0})
    """

    assert vertex_or_edge in ["vertex", "edge"], "vertex_or_edge has to be either 'vertex' or 'edge'"
    for t in transform:
        new_val = []

        if vertex_or_edge == "vertex":
            iterate = gr.vs[t["name"]]
        else:
            iterate = gr.es[t["name"]]
        for val in gr.vs[t["name"]]:
            try:
                new_val.append(t["func"](val))
            except TypeError:
                new_val.append(t["default"])
            except ValueError:
                new_val.append(t["default"])

        gr.vs[t["name"]] = new_val

if __name__ == '__main__':
    ml = MultiLayerGraph.load("/Users/dwinter/ownCloud/python_notebooks/GMPG/kommissionen/data/kommissionen.pickle")
    ml.generateMerged_ynws(intervalls=[2], update=False)
    print(ml)