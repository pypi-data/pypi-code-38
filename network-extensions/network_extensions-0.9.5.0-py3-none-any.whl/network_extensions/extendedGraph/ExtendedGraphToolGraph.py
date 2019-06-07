import re
import sre_constants
import tarfile
import tempfile
from itertools import product

import uuid
import happybase
from multiprocessing.pool import Pool

from thriftpy.transport import TTransportException

CACHE = 0
HBASE_MODE = 1
try:
    HBASE  = happybase.Connection('localhost',table_prefix="GEN_GRAPH")
except TTransportException:
    print("NO HBASE")

#from memory_profiler import profile
import igraph

import pickle
import logging
logger = logging.getLogger()
import os
from tqdm import tqdm

from network_extensions.extendedGraph.RedisDataTypes import RList
from network_extensions.igraphx import getA, projectBipartiteParallel

import logging
from graph_tool.all import *


class MergeError(Exception):
    pass


class ExtendedGraph(Graph):
    """Extended Graph keeps attritebutes of nodes in separate list"""
    def __init__(self,**kwargs):
        igraph.Graph.__init__(self,**kwargs) # this will be the simplified graph
        self.edgesByStartYear = None
        self.startYearEdgeAttribute = None  # contains later the attribute name  for start-year at the edges





    def getA(n, attr, val="UN"):
        try:
            return n[attr]
        except KeyError:
            return val

    def calcTop(ng,
                number, func="betweenness", filter_node=None,
                func_edge="edge_betweenness",
                with_value=True,
                displayAttr="lastname",
                displayAttr2="name",
                deleteZero=True,
                **kwargs):
        """berechne die Zentralitätsmße von Kanten und Knoten, sortiere
        dann nach den Werte und gib die durch NUMBER bestimmte Anzahl zurück."""
        if len(ng.vs) == 0:
            return []
        bct_pairs = []

        if "norm_by_nodes" in kwargs:
            norm_by_nodes = kwargs["norm_by_nodes"]
            del kwargs["norm_by_nodes"]
        else:
            norm_by_nodes = False

        vals = getattr(ng, func)(**kwargs)
        if norm_by_nodes:
            no_nodes = len(vals)
            if no_nodes > 2:
                vals = [x / ((no_nodes - 1) * (no_nodes - 2)) for x in vals]

        ng.vs[func] = vals
        for n in ng.vs:

            # n[func]=getattr(n,func)()

            if filter_node is None:
                addPair = True
            else:  # gehe durch die Filter attribute, wenn eine Bedingung erfuellt ist dann wird der Wert hinzugefuegt
                addPair = False
                for filter_key, filter_value in filter_node.items():
                    val = n.get(filter_key, "")
                    if val in filter_value:
                        addPair = True
                        break

            if deleteZero and n[func] == 0:  # don't add zero values
                continue

            if addPair:

                id_attr = getA(n, displayAttr2).strip()

                if with_value:
                    bct_pairs.append(((getA(n, displayAttr), id_attr), n[func]))
                else:
                    bct_pairs.append((getA(n, displayAttr), id_attr))

        bct_pairs_sorted = sorted(bct_pairs, key=lambda x: x[-1])
        bct_pairs_sorted.reverse()

        for e, v in zip(ng.es, getattr(ng, func_edge)()):
            e[func_edge] = v

        return bct_pairs_sorted[0:number]

    def edgeListLongToEdgeList(self,v_attr_name=None):
        elist = [(s,e) for s,e,attr in self.edgeListLong]
        self.add_edges(elist,v_attr_name=v_attr_name)

    def save_extGraph(self,folder,exist_ok=True):

        os.makedirs(folder,exist_ok=exist_ok)

        igraph.write(self,os.path.join(folder,"graph.graphml"))

        if len(self.edgeList) == 0 and len(self.edgeListLong) != 0:
            print("WARNING: edgeList is empty bud edgeListLong not, have you run edgeListLongToEdgeList?")
        #with open(os.path.join(folder,"edgeAttr.pickle"),"wb") as outf:
        #        pickle.dump(self.edgeAttrs,outf)

        bytes_out = pickle.dumps(self.edgeAttrs) # https://stackoverflow.com/questions/31468117/python-3-can-pickle-handle-byte-objects-larger-than-4gb
        max_bytes = 2 ** 31 - 1
        with open(os.path.join(folder, "edgeAttr.pickle"), "wb") as outf:
            for idx in range(0, len(bytes_out), max_bytes):
                outf.write(bytes_out[idx:idx + max_bytes])

        with open(os.path.join(folder,"edgeList.pickle"),"wb") as outf:
                pickle.dump(self.edgeList,outf)
        with open(os.path.join(folder,"multiEdges.pickle"),"wb") as outf:
                pickle.dump(self.multiEdges,outf)

    def get_edgeListLong(self):
        if len(self.edgeListLong) == 0:  # can happen if edgeList ist created directly e.g by loading from file
            for (s,e),attrs in self.edgeAttrs.items():
                for attr in attrs:
                    self.edgeListLong.append((s,e,attr))
        return self.edgeListLong

    @classmethod
    def load_extGraph(cls,folder):
        if not os.path.exists(folder):
            raise FileNotFoundError

        #gr = ExtendedGraph()
        gr  = load_graph(os.path.join(folder,"graph.graphml"))

        gr.__class__ = cls


        try:
            with open(os.path.join(folder, "edgeAttr.pickle"), "rb") as inf:
                gr.edgeAttrs = pickle.load(inf)

        except FileNotFoundError:
            print ("no_edge attr")

        try:
            with open(os.path.join(folder, "edgeList.pickle"), "rb") as inf:
                gr.edgeList = pickle.load(inf)
        except FileNotFoundError:
            print("no_edgelist")

        try:
            with open(os.path.join(folder, "multiEdges.pickle"), "rb") as inf:
                gr.multiEdges =pickle.load(inf)
        except FileNotFoundError:
            print ("no_multiedges")


        for attrs in gr.edgeAttrs.values():
            gr.edgeAttrNames = set()
            for attr in attrs:
                gr.edgeAttrNames.update(attr.keys())
        gr.edgesByStartYear = None
        gr.startYearEdgeAttribute = None  # contains later the attribute for state year at the edges

        gr.get_edgeListLong()

        if len(gr.es) != len(gr.edgeList):
            logging.warning("Import number of edge in the graph not euqal legth of edgeList")
            logging.warning("I will delete the edges and recrea them from edgeattrs")
            gr.es.delete()
            gr.add_edges()

        try:
            gr.saveCaches()
        except:
            pass #not implemented

        return gr

    @classmethod
    def  getGraphFromEdgeAndNodeLists(cls,edgeList=[], nodeDict={}):
        gr = cls()
        if nodeDict is not None:
            for n, attrs in nodeDict.items():
                gr.add_vertex(**attrs)

        elist = set([(s, e) for s, e, attrs in edgeList])
        gr.add_edges(elist)
        gr.set_edgeAttrsDict(edgeList)
        return gr

    @classmethod
    def  getGraphFromEdgeListAndGraph(cls,edgeList=[], graph=None,mode="redis"):
        gr = cls()
        for v in graph.vs:
            gr.add_vertex(**v.attributes())

        if mode == "redis":
            edgeList = RList(key_int=edgeList)
        elist = set([(s, e) for s, e, attrs in edgeList])
        gr.add_edges(elist)
        gr.edgeListLong = edgeList
        gr.set_edgeAttrsDict()
        return gr

    @classmethod
    def projectBipartiteParallel(cls,og, types, inverse=False, safe=True, worker=5,
                                 vattr_name="name", save_intermediate=True,
                             eattr_name=None):

        return projectBipartiteParallel(og,types,inverse=inverse,
                                        safe=safe,worker = worker,
                                        vattr_name=vattr_name,
                                        save_intermediate=save_intermediate,
                                        eattr_name=eattr_name,
                                        only_edges_nodes = True,
                                        extended_graph=cls)

    @classmethod
    def union(cls,g_1, g_2, v_attr_name):
        mapProp = g_2.new_vertex_property("int")

        attr2id = {}
        try:
            attr2id = {v:n for n,v in enumerate(g_1.vertex_properties[v_attr_name])}
        except KeyError:
            logging.warning("vertex property %s not in %s"%(v_attr_name,g_1.vertex_properties.keys()))

        if len(attr2id) == 0:
            return g_2 #g_1

        new = max(attr2id.values()) + 1
        for n in g_2.get_vertices():

            try:
                attr = g_2.vertex_properties[v_attr_name][n]
            except:
                logging.warning("vertex property %s not in %s" % (v_attr_name, g_2.vertex_properties.keys()))
            else:
                try:
                    mapProp[n] = attr2id[attr]
                except KeyError:
                    mapProp[n] = new
                    new +1


        ug = graph_tool.generation.graph_union(g_1, g_2, intersection=mapProp,internal_props=True)
        return ug

    @staticmethod
    def mergeAllGraphsIntervall(graphs, intervall, mergeattr="label",
                                    chooseOnlyNodesInYear=True,
                                    start_attr="startYear",
                                    end_attr="endYear"):
            """
            Fügt alle graphen in intervall zusammen.
            :param dict graphs:Jahresgraphen als Dict.
            :param int intervall: intervalllänge
            :param str mergeattr: defaults zu "label" Attribute an den Knoten, die diese indentifiziert.
            :param int onlyNodesInYear: Falls gesetzt, dann werden alle Knoten gelöscht, wenn sie im entsprechende Jahr nicht existieren
            dazu muss es die Attribute startYear und endYear in den Graphen geben.

            :returns: merged graphs als liste
            """
            if intervall == 1:  # do nothing
                return graphs
            ret = {}
            for y, v in graphs.items():
                if chooseOnlyNodesInYear:
                    onlyNodesInYear = y
                else:
                    onlyNodesInYear = None

                if intervall > 0:
                    ret[y] = ExtendedGraph.mergeGraphs(graphs, range(y, y + intervall),
                                         mergeattr,
                                         onlyNodesInYear=onlyNodesInYear,
                                         start_attr=start_attr,
                                         end_attr=end_attr)
                else:
                    ret[y] = ExtendedGraph.mergeGraphs(graphs, range(y + intervall, y + 1),
                                         mergeattr,
                                         onlyNodesInYear=onlyNodesInYear,
                                         start_attr=start_attr,
                                         end_attr=end_attr
                                         )
                    
            return ret

    @staticmethod
    def replaceInAllGraphs(grs,field,newname,str,replace):
        for y,v in grs.items():
            newvalues = [x.replace(str,replace) for x in v.vertex_properties[field]]
            newattr = v.new_vertex_property("string",newvalues)
            v.vertex_properties[newname] = newattr


    @staticmethod
    def mergeGraphs(graphs, yearList=None, mergeattr="label",
                        onlyNodesInYear=None,
                        start_attr="startYear",
                        end_attr="endYear"):
            """vereinigt alle graphen eines year graph bundles
            :param dict  graph: ein Dict mit Jahr:Graph
            :param list(int) yearList: Liste mit Jahren, die zusammengefasst werden sollen.
            :param int onlyNodesInYear: Falls gesetzt, dann werden alle Knote gelöscht, wenn sie im entsprechende Jahr nicht existieren
            dazu muss es die Attribute startYear und endYear in den Graphen geben.
            :returns: vereinheitlichter Graph
            """

            if yearList is None:
                yearList = list(graphs.keys())

            year_start = max(min(graphs.keys()), min(yearList))



            g = graphs[year_start]  # start with the smalles existing year
            for y in yearList[1:]:
                if y in graphs:
                    try:
                        g = ExtendedGraph.union(g, graphs[y], mergeattr)
                    except MergeError:
                        print("ignore %s" % y)
                else:
                    print("ignore %s"%y)
                    pass  # ignore missing years

            if onlyNodesInYear is None:  # loesche alle Knoten, die am Anfnge
                return g
            else:
                yearNode = g.new_vertex_property("bool")
                for n  in g.vertices():

                    if start_attr in g.vertex_properties  and g.vertex_properties[start_attr][n] is not None and g.vertex_properties[start_attr] != "":
                        try:
                            sy = int(n[start_attr])
                        except ValueError:
                            sy = 0
                    else:
                        sy = 0
                    if end_attr in g.vertex_properties  and g.vertex_properties[end_attr][n] is not None and g.vertex_properties[end_attr] != "":
                        try:
                            ey = int(n[end_attr])
                        except ValueError:
                            ey = 99999
                    else:
                        ey = 99999
                    yearNode[n] =  onlyNodesInYear in range(sy, ey + 1)


                # print(y,delNode)
                #g.delete_vertices(delNode)
                return GraphView(g,vfilt=yearNode)


    @staticmethod
    def projectBipartite(og, field, value):

        print("start - bipartite")

        assert is_bipartite(og) == True, "Graph is not pipartite!"

        year_prop = og.new_edge_property(value_type="int")
        bib_prop = og.new_edge_property(value_type="string")

        for n in tqdm(og.get_vertices()):
            if og.vertex_properties[field][n]  == value:
                continue
            y = og.vertex_properties["year"][n]
            if y != "1977":
                continue
            nb = list(og.get_out_neighbors(n)) + list(og.get_in_neighbors(n))
            nb = list(nb)
            for i,j in product(nb,nb):
                #if i>=j:
                #    continue
                e = og.add_edge(i,j)
                year_prop[e] = og.vertex_properties["year"][n]

                bib_prop[e] = og.vertex_properties["bibcode"][n]

        og.edge_properties["year"] = year_prop
        og.edge_properties["bibcode"] = bib_prop

        newGr = Graph(GraphView(og,vfilt=lambda v : og.vertex_properties[field][v] == value),prune=True)
        return newGr


    @staticmethod
    def isInPeriod(n,og,year,
                   startYear_default=1880,
                   endYear_default=2010,
                   startyear_attr="startYear",
                   endyear_attr="endYear", mode="v"):

        if mode =="v":
            try:
                sy = og.vertex_properties[startyear_attr][n]
                ey = og.vertex_properties[endyear_attr][n]
            except KeyError: #attribute does not exist
                sy = ""
                ey = ""
        else:
            sy = og.edge_properties[startyear_attr][n]
            ey = og.edge_properties[endyear_attr][n]

        try:
            sy = int(sy)
        except ValueError:
            sy = startYear_default

        try:
            ey = int(ey)
        except ValueError:
            ey = endYear_default

        if year in range(sy,ey+1):
            return True
        else:
            return False


    @staticmethod
    def writeGraphsToFile(ynw, fl, pattern="year_network_%s", outputTypes=["graphml"]):

        tf = tarfile.open(fileobj=fl, mode="w:gz")
        for y, g in ynw.items():
            gr = Graph(g,prune=True)
            print(y, len(ynw[y].get_edges()), len(ynw[y].get_vertices()))
            for outputType in outputTypes:
                temp = tempfile.NamedTemporaryFile(delete=False)
                gr.save(temp.name, outputType)

                tf.add(temp.name, arcname=pattern % y + ".%s" % outputType)
                os.unlink(temp.name)
        tf.close()



    def createYearNetworks(self, startyear=None, endyear=None, typ=None,
                           startYear_default=1880, endYear_default=2010, filter_degree_0=True,
                           startyear_attr="startYear", endyear_attr="endYear",
                           startyear_edge_attr=None, endyear_edge_attr=None,
                           include_nodes_without_date=False,
                           simplify=False,
                           combine_edges=None,
                           edgesByStartYear=None,
                           only_edge_list=False,
                           DEBUG=True,
                           worker=1):

        if isinstance(self,list):

            startyear = self[1]
            endyear = self[2]
            startYear_default = self[3]
            endYear_default = self[4]
            filter_degree_0 = self[5]
            startyear_attr = self[6]
            endyear_attr = self[7]
            startyear_edge_attr = self[8]
            endyear_edge_attr = self[9]
            include_nodes_without_date =self[10]
            simplify =self[11]
            combine_edges = self[12]
            edgesByStartYear = self[13]
            only_edge_list = self[14]
            worker = 1
            typ = self[16]
            DEBUG = self[15]
            self = self[0]



        ynw = {}
        if worker > 1:#parellize
            no_years = (endyear-startyear)  + 1
            years_per_worker = no_years/worker
            if years_per_worker != round(years_per_worker):
                years_per_worker += 1
                batches = []
            years_per_worker = round(years_per_worker)
            for period_start in range(startyear,endyear,years_per_worker):
                batches.append([self,period_start,
                                period_start+years_per_worker+1,
                                startYear_default,
                                endYear_default,
                                filter_degree_0,
                                startyear_attr,
                                endyear_attr,
                                startyear_edge_attr,
                                endyear_edge_attr,
                                include_nodes_without_date,
                                simplify,
                                combine_edges,
                                edgesByStartYear,
                                only_edge_list,
                                DEBUG,
                                typ])
            print("I have %s batches!"%len(batches))
            with Pool(len(batches)) as p:
                ret = p.map(ExtendedGraph.createYearNetworks, batches)

            retdict = ret[0]
            for r in ret[1:]:
                retdict.update(r)
            return retdict

        for y in tqdm(range(startyear,endyear)):
            test_vertex = lambda v : ExtendedGraph.isInPeriod(v,self,y,
                                                              startYear_default,
                                                              endYear_default,
                                                              startyear_attr,
                                                              endyear_attr)
            test_edge = lambda v : ExtendedGraph.isInPeriod(v,self,y,
                                                              startYear_default,
                                                              endYear_default,
                                                              startyear_edge_attr,
                                                              endyear_edge_attr,
                                                            mode = "e")

            ynw[y] = GraphView(self,vfilt = test_vertex,efilt = test_edge)
            gr = Graph(ynw[y],prune=True)
            gr.save("/tmp/%s.graphml"%y)

            #print(y,len(ynw[y].get_edges()),len(ynw[y].get_vertices()))
        return ynw


    @classmethod
    def getGraphsFromFile(cls,fl, pattern=".*_network_(.*).graphml", max_no_of_files=400, selectedYears=None,
                              no_content=False):
            """erzeugt den Graphen aus dem year-Graph file, unterstützt alle Formate,
            die von igraph unterstützt werden.
            :param Filehandle:
            :param pattern: matching pattern für die Filenamen ()
            :param list or int selectedYears: selected years
            @returns igraph Graphen
            """

            if selectedYears is not None and isinstance(selectedYears, int):
                selectedYears = [selectedYears]
            logger.debug("open tar file")
            tf = tarfile.open(fileobj=fl, mode="r:gz")

            gr = tf.next()
            graphs = {}
            cnt = 0
            years = []
            logger.debug("Start reading networks")
            while gr is not None:
                if cnt > max_no_of_files: break  # just to be sure not to kill the browser
                cnt += 1
                fn = gr.name
                logger.debug("found: %s"%fn)
                try:
                    yr = re.match(pattern, fn)
                except sre_constants.error:
                    logger.warning("pattern %s not valid!" % pattern)
                    yr = None

                if yr is not None:
                    try:
                        yr = int(yr.group(1))
                    except ValueError:
                        gr = tf.next()
                        continue
                    except IndexError:
                        gr = tf.next()
                        continue
                    logger.debug("got year: %s"%yr)
                    years.append(yr)

                    if selectedYears is not None:
                        if not yr in selectedYears:
                            gr = tf.next()
                            continue

                    if not no_content:
                        fl = tf.extractfile(gr)
                        fn = "%s.graphml" % uuid.uuid4()
                        with open("/tmp/%s" % fn, "wb") as ouf:
                            ouf.write(fl.read())
                        graph = load_graph("/tmp/%s" % fn)
                        os.remove("/tmp/%s" % fn)
                        graphs[yr] = graph

                gr = tf.next()
            tf.close()
            if no_content:
                return years
            else:
                return graphs


if __name__ == "__main__":

        #ynw = getGraphsFromFile(open("/Users/dwinter/Downloads/all_year_persons.ygz", "rb"))
        #ynw_2 = projectBipartiteParallel(ynw[1990], "is_person", worker=1, safe=False)
        print("EDGES")
        with open("../tests/data/ep_short.pickle","rb") as inf:
        #with open("/tmp/ep_short.pickle", "rb") as inf:
            el = pickle.load(inf)
        print("NODES")
        with open("../tests/data/np_short.pickle", "rb") as inf:
        #with open("/tmp/np_short.pickle", "rb") as inf:
                nd = pickle.load(inf)

        gr = ExtendedGraph.getGraphFromEdgeAndNodeLists(edgeList=el,nodeDict=nd)
        gr.set_edgeAttrsDict(el)
        gr.edgeAttrsDictToEdgeAttr(None)
        print ("Now I have to save everything")
        gr.save_extGraph(("/tmp/extgt"))
        gr2 = ExtendedGraph.load_extGraph("/tmp/extgt")

        assert len(gr.vs) == len(gr2.vs), "Nodes, Should be the same"
        assert len(gr.es) == len(gr2.es), "Edges, Should be the same"

        assert len(set(gr.vs["name"]) - set(gr.vs["name"])) == 0, "should be zero"

        assert len(gr.multiEdges) == len(gr2.multiEdges), "should be equal"
        assert len(gr.edgeAttrs)  == len(gr2.edgeAttrs), "should be equal"
        assert len(gr.edgeList) == len(gr2.edgeList), "should be equal"


        print("done")
        #print(gr.es["year"])
