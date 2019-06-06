"""Classes to create a semantic network out of corpus"""
import igraph
import requests
from pysolr import Solr
from tqdm import tqdm

from network_extensions.igraphx.multilayer import MultiLayerGraph, NotCalculatedYetError


class SemanticLayer(MultiLayerGraph):

    def __init__(self,solr_url,*args,**kwargs):
        self.solr = Solr(solr_url)
        super().__init__(*args,**kwargs)

    @staticmethod
    def get_simple_semantic_nw(solr_url,start,threshold=0, max_number_terms = None, end=None, widget = None):

        gr = igraph.Graph()
        phrase_2_node = {}
        if not end:
            end = start #one year

        qs = solr_url + '/tvrh?fl=id&rows=10000000&q=date:[%s-01-01T00:00:00Z TO %s-12-31T23:59:00Z]&tv=true&tv.fl=nounphrase_exact&tv.tf_idf=true&tv.tf=true' % (start, end)

        res = requests.get(qs).json()
        tvs = res["termVectors"]

        cnt = 0

        if widget:
            disable = True
            widget.value = 0
            widget.max = len(tvs)/2
        else:
            disable = False


        for tv_i in tqdm(range(0, len(tvs), 2),disable=disable):
            if widget:
                widget.value += 1
            doc = tvs[tv_i]
            did = gr.vcount()
            gr.add_vertex(doc,label=doc,typ="document")
            doc_node = gr.vs[did]
            cnt += 1
            if len(tvs[tv_i + 1]) < 4:
                continue  # no terms
            vals = tvs[tv_i + 1][3]  # gives the list
            if max_number_terms:
                no_vals = min(max_number_terms,len(vals))
            else:
                no_vals = len(vals)
            for v_i in range(0, no_vals, 2):
                phr = vals[v_i]
                phrase_node = phrase_2_node.get(phr, None)
                if not phrase_node:
                    gr.add_vertex(phr,label=phr,typ="phrase")
                    phrase_node = gr.vs[gr.vcount()-1]
                    phrase_2_node[phr] = phrase_node
                attrs = {}
                for val in range(0, len(vals[v_i + 1]), 2):
                    att = vals[v_i + 1][val]
                    num = vals[v_i + 1][val+1]
                    attrs[att] = num

                if attrs["tf-idf"] > threshold:
                    gr.add_edge(phrase_node, doc_node,**attrs)
        return gr

    def createYearNetworks(self,start,end,
                           threshold=0, max_number_terms= None,widget_years=None, widget_network=None, widget_year_int = None):


        ynw = MultiLayerGraph.YearNetwork()
        if widget_years:
            disable = True
            widget_years.value = 0
        else:
            disable = False

        for y in tqdm(range(start,end),disable=disable):
            if widget_years:
                widget_years.value += 1
                widget_years.max = len(range(start,end))
            if widget_year_int:
                widget_year_int.value = y

            ynw[y] = SemanticLayer.get_simple_semantic_nw(self.solr.url,y,
                                                          threshold,
                                                          max_number_terms=max_number_terms,
                                                          widget = widget_network)

        self._ynws = ynw




    def generateMultiLayer(self, v_attr_name = "label", update = False):

        nw = igraph.Graph()
        nw.vs["label"] = ""

        label_2_nodes = {}
        s_t_2_edges = {}
        for y,gr in self.ynws.items():
            for n in gr.vs:

                label = n["label"]

                node = label_2_nodes.get(label,None)
                if node is None:
                    nid = nw.vcount()
                    nw.add_vertex(**n.attributes())
                    node = nw.vs[nid]
                    node["begins"] = y
                    node["ends"] = y
                    label_2_nodes[label] = node

                node["begins"] = min(y,node["begins"])
                node["ends"] = max(y, node["ends"])

            for e in gr.es:

                label_source = gr.vs["label"][e.source]
                label_target = gr.vs["label"][e.target]

                #faster then find label=XX
                nw_source_index = nw.vs["label"].index(label_source)
                nw_target_index = nw.vs["label"].index(label_target)

                source = nw.vs[nw_source_index]
                target = nw.vs[nw_target_index]

                #source = nw.vs.find(label = label_source)
                #target = nw.vs.find(label = label_target)
                e_new = s_t_2_edges.get((nw_source_index,nw_target_index),None)
                if e_new:
                    #e_new = nw.es.find(_source=source,_target=target)
                    e_new["tf"] += e["tf"]
                else:
                    eid = nw.ecount()
                    nw.add_edge(source,target,**e.attributes())
                    e_new = nw.es[eid]
                    e_new["tf"] = e["tf"]
                    s_t_2_edges[(nw_source_index,nw_target_index)] = e_new
        self._multi_layer = nw

    def copy(self):

        ng = SemanticLayer(solr_url = self.solr.url)
        try:
            ng._ynws = self.ynws.copy()
        except NotCalculatedYetError:
            pass

        try:
            ng._multi_layer = self.multi_layer.copy()
        except NotCalculatedYetError:
            pass

        try:
            ng._merged_ynws = self.merged_ynws.copy()
        except NotCalculatedYetError:
            pass

        return ng



    def save(self,fn):

        solr = self.solr #cannot be saved
        self.solr = None
        super().save(fn)
        self.solr = solr


if __name__ == '__main__':

    solr_url = "http://%s:%s@dw2.mpiwg-berlin.mpg.de:38983/solr/abstracts" % ("solr", "5!7DjpW6")

    cr = SemanticLayer(solr_url)
    cr.createYearNetworks(1925, 1925, max_number_terms= 4)
    #cr.generateMultiLayer()
    #cr.createFigGraph(typ_field=None)
    cr.save("/tmp/test.pickle")


