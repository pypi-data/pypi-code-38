import warnings
import igraph
import math
import matplotlib.patches as mpatches
from builtins import str
import matplotlib

#from network_extensions.igraph_redis import ExtendedRedisGraph
#from network_extensions.ExtendedGraph import ExtendedGraph
#from network_extensions.ExtendedGraph import ExtendedGraph

#try: #TODO improve this handling
#    matplotlib.use("MacOSX")
 #   from matplotlib import pylab
#except:
#    matplotlib.use("ps")
#    from matplotlib import pylab


import tarfile
import re
import logging
from time import time
import sre_constants
import uuid
from itertools import product
from collections import defaultdict, OrderedDict
import numpy as np

from tqdm import tqdm

class NoDataError(Exception):
    pass


logger = logging.getLogger(__name__)


class GraphCache:
    """singleton wird benutzt um berechnete Graphdaten zu cachen"""
    class __GraphCache:  
        graphsStore={}
        
    instance = None
    def __init__(self):
        if not GraphCache.instance:
            GraphCache.instance = GraphCache.__GraphCache()
            
    def __getattr__(self, name):
        return getattr(self.instance, name)

def add_edge_safe(gr,ns_vertex,nm_vertex,node_edge_properties):
        
        edges = gr.es.select(_source=ns_vertex.index,_target=nm_vertex.index)
        for edg in edges:
            shared_items = set(edg.attributes().items()).symmetric_difference(set(node_edge_properties.items()))
            if len(shared_items)==0:
                return False #no adding necessary
        gr.add_edge(ns_vertex,nm_vertex,**node_edge_properties)
       
          
def year_graph(gr,yearStart,yearEnd=None):
    if yearEnd is None:
        yearEnd = yearStart
    gr2 = gr.copy()
    #edges = gr2.es.select(begin_gt=yearEnd)
    edges = gr2.es.select(begin=0) #alle nicht datierten auch raus
    gr2.delete_edges(edges)
    edges = gr2.es.select(end=2050) #alle nicht datierten auch raus
    gr2.delete_edges(edges)
    edges = gr2.es.select(begin_gt=yearEnd)
    gr2.delete_edges(edges)
    edges = gr2.es.select(end_lt=yearStart)
    gr2.delete_edges(edges)
    ns=gr2.vs.select(_degree_lt=1)
    gr2.delete_vertices(ns)
    return gr2



    
def get_edgelist(g,attrs,v_attr):
    ret =[]
    for e in g.es:
        s = v_attr[e.source]
        t = v_attr[e.target]
        attrL =[s,t] + [(v,getA(e,v,"")) for v in attrs] 
        ret.append(tuple(attrL))
    try:
        return set(ret)
    except:
        print("ERROR")
   
def get_merged_edge_list(ml):   
    ret=defaultdict(list)
    for m in ml:
        s=m[0]
        t=m[1]
        
        attrs={}
        for k,v in m[2:]:
            attrs[k]=v
        ret[(s,t)].append(attrs)
        
    return ret
            
def union(g_1, g_2, v_attr_name,e_attr_name = None, typ_field = None):
    """ siehe https://github.com/igraph/igraph/issues/876
    Erzeugt die Vereinigung zweier (gerichteter) Graphen über gemeinsame "v_attr_name".
    Kanten mit gleichen Attribute werden zusammengefasst. Zur Zeit wird ein eventuelles "weight"-Attribute
    herausgefilter.
    
    @param g_1 Graph 1
    @param g_2 Graph 2
    @param v_attr_name Name des Attributes, dass zur eindeutigen Identifikation der Knoten  benutzt werden kann.
    @param typ_field if not only field of the same type are joined identified by the value of typ_field
    
    @returns vereinigten Graphen
    """
    assert v_attr_name in g_1.vs.attribute_names(), "attribute must be in vertex attributelist of graph_1"
    assert v_attr_name in g_2.vs.attribute_names(), "attribute must be in vertex attributelist of graph_2"

    if not typ_field: ## Im not checking this if typ_field is set.
        assert len(set(g_1.vs[v_attr_name])) == len(g_1.vs[v_attr_name]), "Merging attribute must be unique"
        assert len(set(g_2.vs[v_attr_name])) == len(g_2.vs[v_attr_name]), "Merging attribute must be unique"

    if typ_field:
        v_attr_1 = []
        v_attr_2 = []
        #we create a new attr_name
        for t,v in zip(g_1.vs[v_attr_name],g_1.vs[typ_field]):
            v_attr_1.append("%s__%s"%(t,v))

        g_1.vs["__union_tmp"] = v_attr_1

        for t, v in zip(g_2.vs[v_attr_name], g_2.vs[typ_field]):
            v_attr_2.append("%s__%s" % (t, v))

        g_2.vs["__union_tmp"] = v_attr_2

        v_attr_name = "__untion_tmp"

    else:
        v_attr_1 = g_1.vs[v_attr_name]
        v_attr_2 = g_2.vs[v_attr_name]

    attrs = [x for x in g_1.es.attributes() if x != "weight"] #TODO have to deal with weights
    attrs += [x for x in g_2.es.attributes() if x != "weight"]
    attrs = list(set(attrs)) #make unique
    edge_list_by_attribute_1 = get_edgelist(g_1,attrs,v_attr_1)
    edge_list_by_attribute_2 = get_edgelist(g_2,attrs,v_attr_2)
    edge_list_by_attribute_merged  = edge_list_by_attribute_1.union(edge_list_by_attribute_2)

    v_attr_merged = sorted(list(set(g_2.vs[v_attr_name]).union(set(g_1.vs[v_attr_name]))))

    attribute_to_ind = {v_attr_merged:i for i, v_attr_merged in enumerate(v_attr_merged)}

    mergedEdges = get_merged_edge_list(edge_list_by_attribute_merged)
    mergedEdgesList = [(i,j) for i, j in mergedEdges.keys()]  
    edge_list_merged = [ (attribute_to_ind[i], attribute_to_ind[j]) for i, j in mergedEdgesList]


    #logger.debug("dict g1 %s:" % g_1.__dict__)
    graph_merged = g_1.__class__(edge_list_merged,directed=True)
    ## add additiona attributes
    for k,v in g_1.__dict__.items():
        if hasattr(v,"copy"):
            setattr(graph_merged,k,v.copy())
        else:
            setattr(graph_merged, k, v)

    #logger.debug("dict graph_merged %s:" % graph_merged.__dict__)
    add_edges = defaultdict(defaultdict)
    for a in attrs:
        for (e,vs),edge in zip(mergedEdges.items(),graph_merged.es):
            cnt = 0
            for v in vs:
                if cnt == 0:
                    edge[a] = v[a]
                else:
                    try:
                        add_edges[(edge.source,edge.target)][cnt].append((a,v[a]))
                    except KeyError:
                        add_edges[(edge.source, edge.target)][cnt]=[(a,v[a])]

                cnt  += 1

                #graph_merged.es[a]=[mergedEdges[e][a] for e in mergedEdgesList]

    for e,n_vs in add_edges.items():

        for k,vs in n_vs.items():
            d = {x:y for x,y in vs}
            graph_merged.add_edge(e[0],e[1],**d)

    if len(graph_merged.vs) == 0:
        graph_merged.add_vertices(v_attr_merged)
    graph_merged.vs[v_attr_name] = v_attr_merged

    # Include attributes that are in both g_1 and/or g_2. If different attribute values are present in a vertex,
    # then one of g_1 is used

    #logging.debug("now adding attrs")
    #logging.debug(g_2.vs.attributes())
    #logging.debug(g_1.vs.attributes())

    common_attrs = set(g_2.vs.attributes()).union(set(g_1.vs.attributes())).difference([v_attr_name])
    logging.debug(common_attrs)

    for attr_name_other in common_attrs:
        attr_other = dict()

        if attr_name_other in g_2.vertex_attributes():
            for v in g_2.vs():
                attr_other[ attribute_to_ind[v[v_attr_name]]] =  v[attr_name_other]

        if attr_name_other in g_1.vertex_attributes():
            for v in g_1.vs():
                attr_other[ attribute_to_ind[v[v_attr_name]]] = v[attr_name_other]

        graph_merged.vs[attr_name_other] = [attr_other[i] if i in attr_other else None  for i in range(graph_merged.vcount())]

    attrs_set = defaultdict(set)
    dels = []
    if e_attr_name is not None:
        for e in graph_merged.es:

            attr_test =e[e_attr_name]
            if attr_test in attrs_set[(e.source,e.target)]:
                dels.append(e)
            elif attr_test in attrs_set[(e.target,e.source)]:
                dels.append(e)
            else:
                attrs_set[(e.source, e.target)].add(attr_test)

    for e in dels:
        e.delete()

    return graph_merged  

def addProperty(graphproperties,func,graphs,params=None,kwargs={}): 
    for y,graph in graphs.items():    
        
        val = getattr(graph,func)(params,**kwargs)          
        graphproperties[y][func]=val
   

def mergeAllGraphsIntervall(graphs,intervall,mergeattr="label",
                            chooseOnlyNodesInYear=True,
                             start_attr="startYear",
                             end_attr="endYear"):
    """
    Fügt alle graphen in intervall zusammen.
    :param dict graphs:Jahresgraphen als Dict.
    :param int intervall: intervalllänge
    :param str mergeattr: defaults zu "label" Attribute an den Knoten, die diese indentifiziert. 
    :param int chooseOnlyNodesInYear: Falls gesetzt, dann werden alle Knoten gelöscht, wenn sie im entsprechende Jahr nicht existieren
    dazu muss es die Attribute startYear und endYear in den Graphen geben.
    
    :returns: merged graphs als liste 
    """
    if intervall==1: #do nothing
        return graphs
    ret ={}
    for y,v in tqdm(graphs.items()):
        if chooseOnlyNodesInYear:
            onlyNodesInYear = y
        else:
            onlyNodesInYear = None
        
        if intervall>0:
            ret[y]=mergeGraphs(graphs, range(y,y+intervall), 
                               mergeattr,
                               onlyNodesInYear=onlyNodesInYear,
                               start_attr = start_attr,
                               end_attr = end_attr,
                               strict = False)
        else:
            ret[y]=mergeGraphs(graphs, range(y+intervall,y+1), 
                               mergeattr,
                               onlyNodesInYear=onlyNodesInYear,
                               start_attr = start_attr,
                               end_attr = end_attr,
                               strict = False
                               )
        
            
        
    return ret


def simplify(graph,loops=True, create_weight=True):
    orig_attrs = graph.edge_attributes()
    combine = {}
    for n in orig_attrs:
        if isinstance(graph.es[n][0],int) or isinstance(graph.es[n][0],float):
            combine[n] = "sum"
        elif isinstance(graph.es[n][0],bool):
            combine[n] = "sum"
        else:
            combine[n] = "concat"


    #combine = {x: combine_edges for x in orig_attrs}
    if create_weight:
        if not "weight" in orig_attrs:
            combine["weight"] = "sum"
            graph.es["weight"] = 1

    graph.simplify(loops=loops,combine_edges=combine)
    
def  mergeGraphs(graphs,yearList,mergeattr="label",
                 onlyNodesInYear=None,
                 start_attr="startYear",
                 end_attr="endYear",
                 strict = False):
    """vereinigt alle graphen eines year graph bundles
    :param dict  graph: ein Dict mit Jahr:Graph
    :param list(int) yearList: Liste mit Jahren, die zusammengefasst werden sollen.
    :param int onlyNodesInYear: Falls gesetzt, dann werden alle Knoten gelöscht, wenn sie im entsprechende Jahr nicht existieren
    dazu muss es die Attribute startYear und endYear in den Graphen geben.
    :param bool strict: Falls True werden nur Graphen zurückgegeben, die genau in dem Intervall liegen, dass von der yearList definiert
    wird (min(yearList) - max(yearList), d.h. alle Knoten Kanten müssen in dem Intervall beginnen und enden.
    :returns: vereinheitlichter Graph

    """

    year_start = max(min(graphs.keys()), min(yearList))

    g = graphs[year_start]  # start with the smalles existing year
    while not mergeattr in g.vs.attribute_names():
        print("mergeGraphs: %s not in vertex attributes of year %s" % (mergeattr, year_start))
        year_start += 1
        if year_start > max(yearList): #nothing in
            return  igraph.Graph()

        try:
            g = graphs[year_start]
        except KeyError:
            logger.warning("Year %s not in ynw of graphs to be merged!"%year_start)
            g = igraph.Graph()



    for y in yearList[1:]:
        if y in graphs:
            if not mergeattr in graphs[y].vs.attribute_names():
                continue
            g = union(g, graphs[y], mergeattr)

    if onlyNodesInYear is not None: #loesche alle Knoten, die am Anfnge
        delNode=[]

        for n in g.vs:
            if start_attr in g.vs.attributes() and n[start_attr] is not None and n[start_attr] != "":
                try:
                    sy = int(n[start_attr])
                except ValueError:
                    sy = 0
            else:
                sy = 0
            if end_attr in g.vs.attributes() and n[end_attr] is not None and n[end_attr] != "":
                try:
                    ey = int(n[end_attr])
                except ValueError:
                    ey = 99999
            else:
                ey = 99999
            if not onlyNodesInYear in range(sy,ey+1):
                delNode.append(n)
        #print(y,delNode)
        g.delete_vertices(delNode)


    if strict:
        delNode = []
        for n in g.vs:
            try:
                sy = int(n[start_attr])
            except ValueError:
                sy = min(yearList)

            try:
                ey = int(n[end_attr])
            except ValueError:
                ey = max(yearList) + 1
            if sy < min(yearList) or ey > max(yearList) + 1:
                delNode.append(n)

        g.delete_vertices(delNode)

    return g


import tempfile
import os
def writeGraphsToFile(ynw,fl,pattern="year_network_%s",outputTypes=["graphml"]):
    """

    :param ynw: dictionary years --> graphs
    :param fl: filehandle
    :param pattern: pattern for filenames defaults to "year_network_%s"
    :param outputTypes: list of output types defaults to ["graphml"]
    :return:
    """
    
    tf = tarfile.open(fileobj=fl,mode="w:gz")
    for y,g in ynw.items():
        for outputType in outputTypes:
            temp = tempfile.NamedTemporaryFile(delete=False)
            g.write(temp.name,outputType)

            tf.add(temp.name,arcname=pattern%y+".%s"%outputType)
            os.unlink(temp.name)
    tf.close()
    

def getYearsFromFile(fl,pattern=".*_network_(.*).graphml",max_no_of_files=400,selected_years=None):
        """gibt die inm  dem year-Graph file enthaltenen Jahres zurück, unterstützt alle Formate,
        die von igraph unterstützt werden.
        :param Filehandle:
        :param pattern: matching pattern für die Filenamen ()
        :param list or int selected_years: selected years
        @returns list of years
        """      
        return getGraphsFromFile(fl,pattern=pattern,max_no_of_files=max_no_of_files,selected_years=selected_years,no_content=True)



def getGraphsFromFile(fl,
                      pattern=".*_network_(.*).graphml",
                      max_no_of_files=400,
                      selectedYears=None,
                      no_content=False):
    warnings.warn("deprecated", DeprecationWarning)

    return loadGraphsFromFile(fl, pattern=pattern,
                       max_no_of_files=max_no_of_files,
                       selectedYears=selectedYears,
                       no_content=no_content)


def loadGraphsFromFile(fl,pattern=".*_network_(.*).graphml",max_no_of_files=400,selectedYears=None,no_content=False):
        """erzeugt den Graphen aus dem year-Graph file, unterstützt alle Formate,
        die von igraph unterstützt werden.
        :param Filehandle:
        :param pattern: matching pattern für die Filenamen ()
        :param list or int selectedYears: selected years
        @returns igraph Graphen
        """

        if selectedYears is not None and isinstance(selectedYears,int):
            selectedYears=[selectedYears]

        tf = tarfile.open(fileobj=fl,mode="r:gz")


        gr = tf.next()
        graphs={}
        cnt=0
        years=[]
        while gr is not None:
            if cnt>max_no_of_files : break #just to be sure not to kill the browser
            cnt+=1
            fn = gr.name
            try:
                yr = re.match(pattern,fn)

            except sre_constants.error:
                logger.warning("pattern %s not valid!"%pattern)
                yr = None
            if yr is not None:
                try:
                    yr=int(yr.group(1))
                except ValueError:
                    gr = tf.next()
                    continue
                except IndexError:
                    gr = tf.next()
                    continue
                years.append(yr)

                if selectedYears is not None:
                    if not yr in selectedYears:
                        gr = tf.next()
                        continue



                if not no_content:
                    fl = tf.extractfile(gr)
                    fn = "%s.graphml"%uuid.uuid4()
                    with open("/tmp/%s"%fn,"wb") as ouf:
                        ouf.write(fl.read())
                    graph = igraph.read("/tmp/%s"%fn)
                    os.remove("/tmp/%s"%fn)
                    graphs[yr]=graph

            gr = tf.next()
        tf.close()
        if no_content:
            return years
        else:
            return graphs


def projectBipartiteProcess(data):
    # gets #repeat i Zeilen, d.h. alle articles mit links to persons, nodes_list alle nodes with links p_l liste der article
    start_time = time()

    inc = data[0] #Zeilen to check (each row is an article with persons linked
    nodes_list = data[1] #all nodes with links per article
    p_l = data[2] #all nodes (articles)
    safe = data[3]
    og = igraph.read("/tmp/ogr.picklez")
    #ng = igraph.Graph(directed=True)
    new_nodes = {}
    new_edges = []
    if safe:
        print("safe mode can be very slow!")

    for i in tqdm(inc):

        # gehe durch alle Spalten der Incidenz-Matrix


        nodes = nodes_list[i]
        person = og.vs[p_l[i]]
        done = set()
        for s, e in product(nodes, nodes):
            if s > e:
                try:
                    #s_n = ng.vs.find(name=og.vs[s]["name"])
                    s_n = new_nodes[og.vs[s]["name"]]
                except KeyError:
                    #ng.add_vertex(**og.vs[s].attributes())
                    #s_n = ng.vs.find(name=og.vs[s]["name"])
                    new_nodes[og.vs[s]["name"]] = og.vs[s].attributes()
                    s_n = new_nodes[og.vs[s]["name"]]

                try:
                    #e_n = ng.vs.find(name=og.vs[e]["name"])
                    e_n = new_nodes[og.vs[e]["name"]]
                except KeyError:
                    #ng.add_vertex(**og.vs[e].attributes())
                    new_nodes[og.vs[e]["name"]] = og.vs[e].attributes()
                    s_n = new_nodes[og.vs[e]["name"]]
                new_edge_attributes = person.attributes().copy()

                # create separate edges for each existing edge

                for eg1, eg2 in product(og.es.select(_between=([s], [person.index])),
                                        og.es.select(_between=([e], [person.index]))):
                    new_edge_attributes = person.attributes().copy()
                    for k, v in eg1.attributes().items():
                        new_edge_attributes["s_m_%s" % k] = v
                    for k, v in eg2.attributes().items():
                        new_edge_attributes["m_e_%s" % k] = v

                    if safe:
                        add_edge_safe(ng, s_n["name"], e_n["name"], new_edge_attributes)
                    else:
                        #ng.add_edge(s_n, e_n, **new_edge_attributes)
                        new_edges.append((s_n["name"], e_n["name"], new_edge_attributes))
                    # ng.add_edge(s_n,e_n,**new_edge_attributes)

            elif s == e:
                if s in done:
                    continue
                done.add(s)
                try:
                    #s_n = ng.vs.find(name=og.vs[s]["name"])
                    s_n = new_nodes[og.vs[s]["name"]]
                except KeyError:
                    #ng.add_vertex(**og.vs[s].attributes())
                    #s_n = ng.vs.find(name=og.vs[s]["name"])
                    new_nodes[og.vs[s]["name"]] = og.vs[s].attributes()
                    s_n = new_nodes[og.vs[s]["name"]]

                try:
                    for eg in og.es.select(_between=([s], [person.index])):
                        new_edge_attributes = person.attributes().copy()
                        for k, v in eg.attributes().items():
                            new_edge_attributes["s_m_%s" % k] = v
                        if safe:
                            add_edge_safe(ng, s_n["name"], s_n["name"], new_edge_attributes)
                        else:
                            #ng.add_edge(s_n, s_n, **new_edge_attributes)
                            new_edges.append((s_n["name"], s_n["name"], new_edge_attributes))

                        # ng.add_edge(s_n,s_n,**new_edge_attributes)
                except:
                    print(s, person.index)

                # ng.add_edge(s,e,**new_edge_attributes)

    #for s_n,e_n, attrs in tqdm(new_edges):
    #    ng.add_edge(s_n, e_n, **attrs)

    return new_edges,new_nodes, time() - start_time

def projectBipartiteProcess2(data):
    # gets #repeat i Zeilen, d.h. alle articles mit links to persons, nodes_list alle nodes with links p_l liste der article
    start_time = time()
    inc = data[0] #Zeilen to check (each row is an article with persons linked
    nodes_list = data[1] #all nodes with links per article
    p_l = data[2] #all nodes (articles)
    safe = data[3]
    og = igraph.read("/tmp/ogr.picklez")
    ng = igraph.Graph(directed=True)
    new_nodes = {}
    new_edges = []
    if safe:
        print("safe mode can be very slow!")

    for i in tqdm(inc):

        # gehe durch alle Spalten der Incidenz-Matrix


        nodes = nodes_list[i]
        person = og.vs[p_l[i]]
        done = set()
        for s, e in product(nodes, nodes):
            if s > e:
                try:
                    s_n = ng.vs.find(name=og.vs[s]["name"])
                    #s_n = new_nodes[og.vs[s]["name"]]
                except ValueError:
                    ng.add_vertex(**og.vs[s].attributes())
                    s_n = ng.vs.find(name=og.vs[s]["name"])
                    #new_nodes[og.vs[s]["name"]] = og.vs[s].attributes()
                    #s_n = new_nodes[og.vs[s]["name"]]

                try:
                    e_n = ng.vs.find(name=og.vs[e]["name"])
                    #e_n = new_nodes[og.vs[e]["name"]]
                except ValueError:
                    ng.add_vertex(**og.vs[e].attributes())
                    #new_nodes[og.vs[e]["name"]] = og.vs[e].attributes()
                    #s_n = new_nodes[og.vs[e]["name"]]
                new_edge_attributes = person.attributes().copy()

                # create separate edges for each existing edge

                for eg1, eg2 in product(og.es.select(_between=([s], [person.index])),
                                        og.es.select(_between=([e], [person.index]))):
                    new_edge_attributes = person.attributes().copy()
                    for k, v in eg1.attributes().items():
                        new_edge_attributes["s_m_%s" % k] = v
                    for k, v in eg2.attributes().items():
                        new_edge_attributes["m_e_%s" % k] = v

                    if safe:
                        add_edge_safe(ng, s_n["name"], e_n["name"], new_edge_attributes)
                    else:
                        ng.add_edge(s_n, e_n, **new_edge_attributes)
                        #new_edges.append((s_n["name"], e_n["name"], new_edge_attributes))
                    # ng.add_edge(s_n,e_n,**new_edge_attributes)

            elif s == e:
                if s in done:
                    continue
                done.add(s)
                try:
                    s_n = ng.vs.find(name=og.vs[s]["name"])
                    #s_n = new_nodes[og.vs[s]["name"]]
                except KeyError:
                    ng.add_vertex(**og.vs[s].attributes())
                    s_n = ng.vs.find(name=og.vs[s]["name"])
                    #new_nodes[og.vs[s]["name"]] = og.vs[s].attributes()
                    #s_n = new_nodes[og.vs[s]["name"]]

                try:
                    for eg in og.es.select(_between=([s], [person.index])):
                        new_edge_attributes = person.attributes().copy()
                        for k, v in eg.attributes().items():
                            new_edge_attributes["s_m_%s" % k] = v
                        if safe:
                            add_edge_safe(ng, s_n["name"], s_n["name"], new_edge_attributes)
                        else:
                            ng.add_edge(s_n, s_n, **new_edge_attributes)
                            #new_edges.append((s_n["name"], s_n["name"], new_edge_attributes))

                        # ng.add_edge(s_n,s_n,**new_edge_attributes)
                except:
                    print(s, person.index)

                # ng.add_edge(s,e,**new_edge_attributes)

    for s_n,e_n, attrs in tqdm(new_edges):
        ng.add_edge(s_n, e_n, **attrs)

    return ng,time()-start_time


def projectBipartiteParallel(og,types,inverse=False,safe=True,
                             worker = 5,
                             vattr_name="name",
                             save_intermediate=True,
                             eattr_name=None,
                             only_edges_nodes = False,
                             extended_graph=None):

    """

    :param og: graph
    :param types: name of a boolean vertex attribute, if this is true than the node is part of the projection
    :param inverse: instead of choosing the set of nodes where types is true choose the inverse
    :param safe:
    :param worker:
    :param vattr_name:
    :param save_intermediate:
    :param eattr_name:
    :param only_edges_nodes:
    :param extended_graph:
    :return:
    """



    print("start - bipartite")

    assert og.is_bipartite() == True, "Graph is not pipartite!"

    if inverse:
        og.vs["NOT_%s" % types] = [not x for x in og.vs[types]]
        types = "NOT_%s" % types

    inc, p_l, r_l = og.get_incidence(types)

    # first find all nodes for the projection which have non zero entries in incidence matrix
    nodes_list = []

    igraph.write(og,"/tmp/ogr.picklez")
    print("start creating batches")
    for rs in inc: #gehe duch slle spalten (not types - e.g. if person - article and selected type is person than go through articles
        nodes = [r_l[r] for r in range(0, len(rs)) if rs[r] > 0] #store all nodes - (person which have links to articles)
        nodes_list.append(nodes)


    data = []
    for i in tqdm(chunks(range(0,len(inc)),int(len(inc)/worker)+1)):
        #print("ch",i)
        data.append([i,nodes_list,p_l,safe])  #repeat i Zeilen, d.h. alle articles mit links to persons, nodes_list alle nodes with links p_l liste der article

    if len(data) == 0:
        raise NoDataError

    with Pool(len(data)) as p:
        graphs = p.map(projectBipartiteProcess,data)

    ret_gr = graphs[0]
    #if save_intermediate:
    #    path = "/tmp/intermediate/%s/"%uuid.uuid4().urn
    #   os.makedirs(path)

    #    for i in range(0,len(graphs)):
    #        graphs[i].write(path+"%s.graphml"%i)


    #for gr in graphs[1:]:
#
    #    try:
    #        ret_gr = union(ret_gr, gr, vattr_name,eattr_name)
    #    except AssertionError:
    #        print(ret_gr.vs[vattr_name])
    #        print(gr.vs[vattr_name])

    #return ret_gr
    all_edges = []
    all_nodes = {}
    for edges,nodes,time in graphs:
        all_edges += edges
        all_nodes.update(nodes)
        print("Time:%s" % time)

    #create nodes


    if only_edges_nodes or extended_graph:

        if extended_graph is not None:

            return extended_graph.getGraphFromEdgeAndNodeLists(edgeList=all_edges, nodeDict=all_nodes)

        return all_nodes,all_edges

    graph = igraph.Graph()


    print("nodes")
    for n,attr in tqdm(all_nodes.items()):
        graph.add_vertex(**attr)
    print("edges")
    for s,e,edge_attr in tqdm(all_edges):
        graph.add_edge(s,e,**edge_attr)

    return graph


def projectBipartiteParallel2(og,types,inverse=False,safe=True,worker = 5,vattr_name="name",save_intermediate=True,eattr_name=None):
    print("start - bipartite")

    assert og.is_bipartite() == True, "Graph is not pipartite!"

    if inverse:
        og.vs["NOT_%s" % types] = [not x for x in og.vs[types]]
        types = "NOT_%s" % types
    print("create_inc")
    inc, p_l, r_l = og.get_incidence(types)

    # first find all nodes for the projection which have non zero entries in incidence matrix
    nodes_list = []

    igraph.write(og,"/tmp/ogr.picklez")
    print("start creating batches")
    #Zähle wie viele links in jeder Zeile
    cnt_links = {}
    for rs_cnt in tqdm(range(0,len(inc))): #gehe duch slle spalten (not types - e.g. if person - article and selected type is person than go through articles
        rs = inc[rs_cnt]
        nodes = [r_l[r] for r in range(0, len(rs)) if rs[r] > 0] #store all nodes - (person which have links to articles)
        nodes_list.append(nodes)
        cnt_links[rs_cnt] = len(nodes)

    #gesamtsumme
    all_links = sum(cnt_links.values())
    # I want to distribute them evenly
    nums_per_worker = int(all_links/worker)
    #now create chunks accordinly
    print("We have: %s per worker"%nums_per_worker)
    data = []
    current_nodes_list = []
    current_link_count = 0
    for i in tqdm(range(0,len(inc))):
        current_link_count +=  cnt_links[i]
        current_nodes_list.append(i)
        #print(current_link_count,nums_per_worker)
        if current_link_count >  nums_per_worker:
            data.append([current_nodes_list, nodes_list, p_l, safe])
            current_nodes_list = []
            current_link_count = 0

    data.append([current_nodes_list, nodes_list, p_l, safe]) #add whats left
       #print("ch",i)
        #data.append([i,nodes_list,p_l,safe])  #repeat i Zeilen, d.h. alle articles mit links to persons, nodes_list alle nodes with links p_l liste der article

    if len(data) == 0:
        raise NoDataError
    print("We have to run  %s  workers"%len(data))

    if len(data) == 1:
        graphs = [projectBipartiteProcess2(data[0])] #don't bother with a process
    else:
        with Pool(len(data)) as p:
            graphs = p.map(projectBipartiteProcess2,data)

    ret_gr = graphs[0]
    if save_intermediate:
        path = "/tmp/intermediate/%s/"%uuid.uuid4().urn
        os.makedirs(path)

        for i in range(0,len(graphs)):
            graphs[i].write(path+"%s.graphml"%i)


    for gr in graphs[1:]:

        try:
            ret_gr = union(ret_gr, gr, vattr_name,eattr_name)
        except AssertionError:
            print(ret_gr.vs[vattr_name])
            print(gr.vs[vattr_name])

    return ret_gr




def projectBipartite(og,types,inverse=False,progressBar=None,tqdm=None,safe=True):
    """
    :param og: Network
    :param types:
    :param inverse:
    :param progressBar:
    :param tqdm:
    :param safe:
    :return:
    """

    assert og.is_bipartite() == True, "Graph is not bipartite!"
    iter = None
    if inverse:
        og.vs["NOT_%s"%types]=[not x for x in og.vs[types]]
        types = "NOT_%s"%types

    inc,p_l,r_l=og.get_incidence(types)


    #first find all nodes for the projection which have non zero entries in incidence matrix
    nodes_list=[]
    for rs in inc:
        nodes=[r_l[r] for r in  range(0,len(rs)) if rs[r]>0]
        nodes_list.append(nodes)
    ng = igraph.Graph(directed=True)


    if progressBar is not None:
            progressBar.max=len(inc)
            progressBar.value=0

            try: # try a different method in addition
                progressBar.max_value=len(inc)
                progressBar.update(0)
                has_update=True
            except:
                has_update=False
                pass

            iter=range(0,len(inc))

    if tqdm is not None:
        iter = tqdm(range(0,len(inc)))

    assert iter is not  None, "Either tqdm or progressbar has to be set"

    for i in iter:

        #gehe durch alle Spalten der Incidenz-Matrix
        if progressBar is not None:
            progressBar.value+=1
            if has_update:
                progressBar.update(progressBar.value)

        nodes=nodes_list[i]
        person = og.vs[p_l[i]]

        done=set()
        for s,e in product(nodes,nodes):
            if s>e:
                try:
                    s_n = ng.vs.find(name=og.vs[s]["name"])
                except ValueError:
                    ng.add_vertex(**og.vs[s].attributes())
                    s_n = ng.vs.find(name=og.vs[s]["name"])
                try:
                    e_n = ng.vs.find(name=og.vs[e]["name"])

                except ValueError:
                    ng.add_vertex(**og.vs[e].attributes())
                    e_n = ng.vs.find(name=og.vs[e]["name"])

                new_edge_attributes=person.attributes().copy()

                #create separate edges for each existing edge

                for eg1,eg2 in product(og.es.select(_between=([s],[person.index])),
                                       og.es.select(_between=([e],[person.index]))):
                    new_edge_attributes=person.attributes().copy()
                    for k,v in eg1.attributes().items():
                        new_edge_attributes["s_m_%s"%k]=v
                    for k,v in eg2.attributes().items():
                        new_edge_attributes["m_e_%s"%k]=v

                    if safe:
                        add_edge_safe(ng, s_n,e_n,new_edge_attributes)
                    else:
                        ng.add_edge(s_n,e_n,**new_edge_attributes)
                    #ng.add_edge(s_n,e_n,**new_edge_attributes)

            elif s==e:
                if s in done:
                    continue
                done.add(s)
                try:
                    s_n = ng.vs.find(name=og.vs[s]["name"])
                except ValueError:
                    ng.add_vertex(**og.vs[s].attributes())
                    s_n = ng.vs.find(name=og.vs[s]["name"])

                try:
                    for eg in og.es.select(_between=([s],[person.index])):
                        new_edge_attributes=person.attributes().copy()
                        for k,v in eg.attributes().items():
                            new_edge_attributes["s_m_%s"%k]=v
                        add_edge_safe(ng, s_n,s_n,new_edge_attributes)
                        #ng.add_edge(s_n,s_n,**new_edge_attributes)
                except:
                    print(s,person.index)


                #ng.add_edge(s,e,**new_edge_attributes)

    return ng



from multiprocessing import Pool


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def createYearNetworksParallel(ng,startyear,endyear,worker=6, **kwargs):
    """
    Creates networks per year, parallelized.
    for the keyword afruments and defaults see.
    @see createYearNetwork

    :param ng: network for details @see createYearNetwork
    :param startyear: integer for start year
    :param endyear: integer for end year
    :param worker: number of workers in parallel
    :param kwargs:  @see createYearNetwork
    :return: dictionary years and network
    """

    years = range(startyear,endyear)

    data = []

    ng_data = ng.write_picklez("/tmp/gr.picklez")

    for y in chunks(years,int(len(years)/worker)):


        data.append([y[0],y[-1]+1,kwargs])

    with Pool(len(data)) as p:
        ret = p.map(createYearNetworksProcess,data)


    retdict = ret[0]
    for r in ret[1:]:
        retdict.update(r)
    return retdict

def createYearNetworksProcess(data):
    ng = igraph.read("/tmp/gr.picklez")

    return createYearNetworks(ng,data[0],data[1],**data[2])


def createYearNetworks(ng,startyear,endyear,typ=None,
                       startYear_default=1880,endYear_default=2010,offset_year=0,filter_degree_0=True,
                       progressBar=None,tqdm=None,startyear_attr="startYear",endyear_attr="endYear",
                       startyear_edge_attr="from_year",endyear_edge_attr="to_year",
                       include_nodes_without_date=False,
                       simplify=False,
                       combine_edges=None):
    """

    :param ng:
    :param startyear:
    :param endyear:
    :param typ:
    :param startYear_default:
    :param endYear_default:
    :param offset_year:
    :param filter_degree_0: deletes all nodes with degree == 0, defaults to true
    :param progressBar:
    :param tqdm:
    :param startyear_attr: attribute which contains the begin of existence of a node (defaults to startYear)
    :param endyear_attr: attribute which contains the begin of existence of a node (defaults to endYear)
    :param startyear_edge_attr:
    :param endyear_edge_attr:
    :param include_nodes_without_date: Keeps node in the graph if they don't have date (defaults to false)
    :param simplify:
    :param combine_edges:
    :return:
    """
    ynw={}
    ng_an = ng.copy()


    if progressBar is not None:
            progressBar.max=endyear
            progressBar.min=startyear
            
            try: # try a different method in addition
                progressBar.max_value=endyear
                progressBar.min_value=startyear
                progressBar.update(startyear)
                has_update=True
            except:
                has_update=False
                pass

            iter = range(startyear,endyear)

    if tqdm is None and progressBar is None:
        from tqdm import tqdm

    if tqdm is not None:
        iter = tqdm(range(startyear, endyear))

    for y in iter:
        #print(y)
        logger.debug("Year %s"%y)
        if progressBar is not None:
            progressBar.value=y
            if has_update:
                progressBar.update(progressBar.value)

        nw = ng.__class__(directed=True)
        old_ids = {}
        logger.debug("new nw type: %s"%type(nw))
        ## add additiona attributes
        for k, v in ng.__dict__.items():
            if v:
                if hasattr(v,"copy"):
                    setattr(nw, k, v.copy())
                else:
                    setattr(nw, k, v)

        #nw = igraph.Graph(directed=True)
        #erst alle nodes im zeitraum
        
        for node in ng_an.vs:
            
            if typ is not None and node["type"]!=typ:
              
                ng_an.delete_vertices([node])
                continue

            #print (ng_an.node[node]["type"])
            try:
                sy = node[startyear_attr]
                if sy is None or sy == "None": #the latter happens if I save a graph with none value and load agaisn
                    sy=startYear_default
            except KeyError:
                sy=startYear_default
                
            try:
                ey = node[endyear_attr]
                if ey is None or ey == "None":
                    ey = endYear_default
            except KeyError:
                ey = endYear_default
  
            if str(sy).lower()=="no" or str(sy).lower()=="" or str(sy).lower() == "none":
                #dont Include him/she in the YearNetWork
                if not include_nodes_without_date:
                    continue
                else:
                    sy=startYear_default
           
            if str(ey).lower() == "no" or str(ey).strip() == "" or str(ey).lower() == "none":
                ey=endYear_default


            try:
                if math.isnan(float(ey)):
                    ey = endYear_default
            except TypeError:
                print(ey)
                raise TypeError(ey)

            ey = int(ey)
            sy = int(sy)
            #print(sy,ey)
            if y in range(sy,ey+1):
                attrs = node.attributes()
                vid = nw.vcount()
                nw.add_vertex(old_id=node.index,**node.attributes())
                old_ids[node.index] = nw.vs[vid]
        #jetzt alle Kanten:
        for e in ng_an.es:
            try:
                sy = e[startyear_edge_attr]
            except KeyError:
                sy = startYear_default
            
            try:
                ey = e[endyear_edge_attr]
            except KeyError:
                ey = endYear_default
                
                ## it can be happen that sy,ey is from a merged graph in this case it has to be splitted
            
            ey=str(ey)
            sy=str(sy)

            for sy,ey in zip(sy.split(";"),ey.split(";")):

                if sy is None or sy == "None":  #happens if I save and load a none value with save graph.
                    sy = startYear_default
                if ey is None or ey == "None":
                    ey = endYear_default

                #logger.debug(e.attributes())


                if isinstance(sy, str):
                    sy=sy.replace("?","")
                    if sy == "":
                        sy=startYear_default

                    try:
                        sy = int(float(sy))
                    except:
                        sy = startYear_default

                if isinstance(ey, str):
                    ey = ey.replace("?","")
         
                    if ey.strip() =="" or ey.strip()=="no":
                        ey=endYear_default
                    
                    if ey=="present":
                        ey=endYear_default
                    
                    try:
                        ey = int(float(ey) )  
                    except ValueError:
                        ey=endYear_default

                if ey is None:
                    ey = endYear_default  
                    
                if sy is None:
                    sy = startYear_default
                    
                orig_ey = int (ey)
                ey = int(ey) + offset_year



                if y in range(int(sy),int(ey)+1):
                    
                    try:

                        #e_s = nw.vs.find(old_id=e.source)
                        #e_t = nw.vs.find(old_id=e.target)
                        e_s = old_ids[e.source]
                        e_t = old_ids[e.target]

                        nw.add_edge(e_s,e_t,**e.attributes())

                    except ValueError:
                        pass #TODO Wenn die Vertices nicht existieren wird ein Fehler geworfen, dieses passiert, da Kanten und Knoten Laufzeiten nicht übereinstimmen müssen, und der Knoten
                            # für das Jahr nicht angelegt wurde.
                    except KeyError:
                        pass
            
        if filter_degree_0:
            deln = nw.vs.select(_degree=0)
            nw.delete_vertices(deln)
        
        #print(y,len(nw.vs))
        if simplify:
            logger.debug("simplify")
            nw.simplify(multiple=True, loops=True, combine_edges=combine_edges)
            logger.debug("new nw type: %s" % type(nw))
        ynw[y]=nw

    return ynw

def getA(n,attr,val="UN"):
    try:
        return n[attr]
    except KeyError:
        return val
    

def calcTop(ng,
            number,func="betweenness",filter_node=None,
            func_edge="edge_betweenness",
            with_value=True,
            displayAttr="lastname",
            displayAttr2="name",
            deleteZero = True,
            normalize = None,
            **kwargs):
    """berechne die Zentralitätsmße von Kanten und Knoten, sortiere 
    dann nach den Werte und gib die durch NUMBER bestimmte Anzahl zurück."""
    if len(ng.vs) == 0:
        return []
    bct_pairs=[]
    
    if "norm_by_nodes" in kwargs:
        norm_by_nodes = kwargs["norm_by_nodes"]
        del kwargs["norm_by_nodes"]
    else:
        norm_by_nodes = False

    vals = getattr(ng,func)(**kwargs)
    if norm_by_nodes:
        no_nodes = len(vals)
        if no_nodes>2:
            vals = [x/((no_nodes-1)*(no_nodes-2)) for x in vals]

    if normalize == "mean":
        vals = vals - np.mean(vals)
    elif normalize == "median":
        vals = vals - np.median(vals)

    ng.vs[func] = vals
    for n in ng.vs:
      
        #n[func]=getattr(n,func)()
       
        if filter_node is None:
            addPair = True
        else: #gehe durch die Filter attribute, wenn eine Bedingung erfuellt ist dann wird der Wert hinzugefuegt
            addPair = False
            for filter_key,filter_value in filter_node.items():
                val = n.get(filter_key,"")
                if val in filter_value:
                    addPair = True
                    break
        
        if deleteZero and n[func] == 0: #don't add zero values
            continue
            
        if addPair:
                
                id_attr=getA(n,displayAttr2).strip()
                        
                if with_value:
                    bct_pairs.append(( (getA(n,displayAttr),id_attr),n[func]) )
                else:
                    bct_pairs.append(( getA(n,displayAttr),id_attr))
            
    bct_pairs_sorted = sorted(bct_pairs, key=lambda x: x[-1])
    bct_pairs_sorted.reverse()
   
   
    for e,v in zip(ng.es,getattr(ng,func_edge)()):
            e[func_edge]=v
   
    return bct_pairs_sorted[0:number]
    
def calcTopsForYears(ynw,func="betweenness",max_len=20,filter_node=None,
                     with_value=True,
                     displayAttr="lastname",
                     progressBar=None,
                     displayAttr2="name",
                     deleteZero = True,
                     normalize = None,
                     **kwargs):
    tops={}
  
  
    
    if progressBar is not None:
            progressBar.max=len(ynw.keys())
            progressBar.value=0
            
            try: # try a different method in addition
                progressBar.max_value=len(ynw.keys())
                progressBar.update(0)
                has_update=True
            except:
                has_update=False
                pass
                
    tops = defaultdict(dict)    
    for y in ynw.keys():
        if progressBar is not None:
            progressBar.value+=1
            if has_update:
                progressBar.update(progressBar.value)
                
        
       
        if isinstance(ynw[y], dict): #we can also pass a set of graphs (like all + largest component per year)
           
            for k  in ynw[y]:
                tops[k][y]  = calcTop(ynw[y][k],max_len,func=func,filter_node=filter_node,
                           with_value=with_value,
                           displayAttr=displayAttr,
                           displayAttr2=displayAttr2,
                           deleteZero = deleteZero,
                           normalize = normalize,
                           **kwargs)
         
        else:
                tops[y]  = calcTop(ynw[y],max_len,func=func,filter_node=filter_node,
                                   with_value=with_value,
                                   displayAttr=displayAttr,
                                   displayAttr2=displayAttr2,
                                   deleteZero=deleteZero,
                                   normalize = normalize,
                                   **kwargs)
                 
        #print(pandas.DataFrame(tops[y][0:10]))
    
    return tops


def generateMatrix(tops):
    ma = {}
    for y in tops.keys():
        for person,val in tops[y]:
            vals = ma.get(person,{})
            vals[y]=val
            ma[person]=vals
    return ma

def generateMa_rank_old(tops, max_val = 20):
    ma_rank={}
    for y in tops.keys():

        for person,val in tops[y]:
            vals = ma_rank.get(person,{})
            vals[y]=20-tops[y].index((person,val)) #20 Punkte für rang 1, 19 für Rang 2 ..
            #print (tops[y].index((person,val)))
            ma_rank[person]=vals
    
    return ma_rank

def generateMa_rank(tops,verbose = False, max_val = 20):
    ma_rank={}
   
    for y in tops.keys():
        if verbose : print (y)
        #print(y)

        # generate not to big bins for each year
        d2 = [x[1] for x in  tops[y]]
        if len(d2) == 0:
            continue
        bins = 1
        if len(d2)> 10:
            max_cnt = len(d2)/10
        else:
            max_cnt = len(d2)
        cnt=max_cnt+1
        h = np.histogram(d2,bins=bins)

        while cnt > max_cnt and bins < int(len(d2)/3):
            #print(y,cnt,max_cnt)
            bins+=1
            h = np.histogram(d2,bins=bins)
            cnt = max(h[0])
            #print(cnt)

        if verbose : print(h)
        if verbose : print("numberofbins",bins)
        
        for person,val in tops[y]:
            vals = ma_rank.get(person,{})
            cnt=0
            for i in range(len(h[1])-1):
                
                s = h[1][i]
                e = h[1][i+1]
                
                
                if s<=val<e:
                    vals[y]= max_val - cnt # /bins #20 Punkte für rang 1, 19 für Rang 2 ..
                    break       
                vals[y] = cnt # /bins
                cnt+=1
               
                
            #print (tops[y].index((person,val)))
            ma_rank[person]=vals
    
    return ma_rank


def generateMatricesAndCounts(tops,ma_rank=None,ma=None, verbose = False, max_val = 20):

    if ma_rank is None:
        ma_rank = generateMa_rank(tops, verbose=verbose, max_val= max_val)
    if ma is None:
        ma = generateMatrix(tops)

    personCount, personMaxCount = getCountsOfPersons(ma_rank)

    return ma, ma_rank, personCount, personMaxCount

def plotTopEntries2(tops,ma_rank=None,ma=None,
                     numbOfOcc = 10,numbOfMaxOcc = 5 ,
                     filename=None, dataverseName=None,
                     dvh=None,dataset=None,position="under",
                     title=None, verbose=True,
                     **kwargs):
    
    if ma_rank is None:
        ma_rank = generateMa_rank(tops,verbose=verbose)
    if ma is None:
        ma = generateMatrix(tops)

    personCount,personMaxCount = getCountsOfPersons(ma_rank)
    plt = plotTopEntries(ma_rank,
                   personCount,personMaxCount,
                   numbOfOcc = numbOfOcc,
                   numbOfMaxOcc = numbOfMaxOcc ,
                   filename=filename, 
                   dataverseName=dataverseName,
                   dvh=dvh,
                   dataset=dataset,
                   position=position,
                   title=title,**kwargs)
    return plt,(ma,ma_rank,personCount,personMaxCount)
        
def plotTopEntries(ma_rank,personCount,personMaxCount,numbOfOcc = 10,numbOfMaxOcc = 5 ,filename=None, 
                   dataverseName=None,dvh=None,
                   dataset=None,position="under",
                   title=None,cmap_name="Set3",
                   **kwargs):
    #numbOfOcc = 15 ## Anzahl, wie of eine Person in den top20 vorkommen muss, damit sie in der Grafik dargestellt werden.
    #numbOfMaxOcc = 5  ## Anzahl, wie of eine Person in den top2 vorkommen muss, damit sie in der Grafik dargestellt werden     
    persons = list(ma_rank.keys())
    #cmap = pylab.get_cmap('Vega20c', len(persons))
    cmap = pylab.get_cmap(cmap_name, 25)
    #color = (for i in pylab.get_cmap('Vega20', len(persons)).values()
    #color=iter(plt.cm.rainbow(np.linspace(0,1,len(persons))))
    patches=[]
    if title is not None:
        plt.title(title)
    cnt=0
    
    if "ax" in kwargs:  
        my_plt = kwargs["ax"] 
        del kwargs["ax"] 
    else:
        my_plt =plt
            
    for i in persons:
       
        c= cmap(cnt)      
        if not i in personCount:
            continue 
        
        if numbOfOcc is None and numbOfMaxOcc is None:
            pass
        elif  numbOfOcc is None and (personMaxCount[i]<numbOfMaxOcc):
            continue
        elif  numbOfMaxOcc is None and (personCount[i]<numbOfOcc):
            continue    
        elif (personCount[i]<numbOfOcc) and (personMaxCount[i]<numbOfMaxOcc):
            continue
       
        cnt+=1
        patches.append(mpatches.Patch(color=c,label=i))
        points = list(ma_rank[i].items())
        points = sorted(points, key=lambda x: x[0])
     
        for i in range(len(points)-1):   
            my_plt.plot((points[i][0],points[i+1][0]),(points[i][1],points[i+1][1]),c=c,**kwargs)

    if position =="under":
        my_plt.legend(handles=patches,
                   bbox_to_anchor=(0,-0.05), 
                   loc="upper left", borderaxespad=0.)
    elif position == "right":
        my_plt.legend(handles=patches,
                    bbox_to_anchor=(1.05, 1), 
                    loc=2, 
                    borderaxespad=0.)
    else:
        raise ValueError("Position has to be 'right' or 'under'")
    if filename is not None:
        my_plt.savefig(filename)
        if dvh is not None:
            dvh.replaceOrCreateFile(dataset,filename,dataverseName)
    #my_plt.show()
    return my_plt

import matplotlib.pyplot as plt
def plot_matrix_as_lines(ma,startyear,endyear,filename=None, dataverseName=None,dvh=None,
                         dataset=None,person_selection=None,
                         threshold=None,
                         deleteZeroLine = True,
                         normalizeByMaxPerLine = False,
                         max_len_label=20,kwargs_plot = {},showTimeLine=True,
                         **kwargs):
    """
    Plots eatch row of the matrix as lines (Spalten sind Jahre)
    :param Matrix ma: Matrix, die dargestellt werdne sollen,
    :param int startyear: Anfangsjahr für die Darstellung
    :param int endyear: Endjahr
    :param str filename (optional): Wenn gesetzt wird das Bild unter dem Namen abgespeichert
    :param str dataverseName  (optional): Name die das Bild im Dataverse erhalten soll.
    :param DataverseHandler dvh (optional): Handler für Dataverse
    :param DataSet dataset  (optional): Dataverse datasetm, wohin das Bild gespeichert werden soll.
    :param person_selection (optional): Entweder eine Liste mit Namen (=Zeilen in der Matrx), die dargestellt werden sollen.
    Oder eine Dict mit den Namen als Keys und die Anfangswert/Endwert. Diese werden dann jeweils als Linien 
    in einer zweiten Graphik dargestellt um z.B. Zeiten mit Kurven verläufen darzustellen.
    """
    years = range(startyear,endyear)
    persons = list(ma.keys())
    person_selection_dict = None
    #print(ma)
    #wenn Personen ausgewählt sind
    
    
    
    if person_selection is not None:   
    
        
        if isinstance(person_selection,dict) and showTimeLine:
            
            # test ob datums angaben bzw. iterierbare start end werte als Values
           
            
            person_selection_dict = person_selection.copy()
            person_selection = list(person_selection.keys())
            f,(ax1,ax2) = plt.subplots(2,1,sharex="col",**kwargs)
            kwargs["ax"] = ax1
            
        else:
            person_selection_dict = None
          
        persons_filtered = []
        name2persons={k[0]:k for k in persons}
        id2persons={k[1]:k for k in persons}
        if not isinstance(person_selection,list):
            raise ValueError("person selection has to be a list")
        for p in person_selection:
            if isinstance(p, list) or isinstance(p,tuple): #liste aus Name und Id:
                if p in persons:
                    persons_filtered.append(p)
            else:
                if p in name2persons:
                    persons_filtered.append(name2persons[p])
                elif p in id2persons:
                    persons_filtered.append(id2persons[p])   
        persons = persons_filtered
    patches =[]
 
    plots ={}
    years_list={}
    for i in persons:
        yrs=[]
        vals=[]
        for x in years:
            if x in ma[i]:
                yrs.append(x)      
                vals.append(ma[i][x])
        
        
        if len(vals) == 0:
            continue
        if threshold is not None:
            if max(vals)<threshold:
                continue 
        
        if (max(vals)-min(vals))  == 0 and deleteZeroLine:
            continue
        
        if max(vals) != 0 and normalizeByMaxPerLine == True:
            vals  = [v/max(vals) for v in vals]
    
        plots[i]=vals
        years_list[i]=yrs
        
    color=iter(plt.cm.Vega20b(np.linspace(0,1,len(plots))))
    colors = []
    pltList = list(plots.keys())
    logger.debug("plotlist: %s"%str(pltList))
    logger.debug("plotlist: %s"%str(kwargs))
    logger.debug("yearslist: %s"%str(years_list))
    logger.debug("plots: %s"%str(plots))
    

    for i in pltList:
        c = next(color)
        colors.append(c)
        if isinstance(i, tuple):
            label=i[0][0:max_len_label]
        else:
            label=i[0][0:max_len_label]
        patches.append(mpatches.Patch(color=c,label=label))
        if "ax" in kwargs:  
            
            kwargs["ax"].plot(years_list[i], plots[i],c=c,**kwargs_plot)
        else:
            #plt.plot(list(years), plots[i],c=c)
            plt.plot(years_list[i], plots[i],c=c,**kwargs_plot)
    if "ax" in kwargs:  
        kwargs["ax"].legend(handles=patches,bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    else:
        plt.legend(handles=patches,bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

    if filename is not None:
        plt.savefig(filename)
        if dvh is not None:
            dvh.replaceOrCreateFile(dataset,filename,dataverseName)
    else:
        #plt.show()
        pass
    
    color=iter(plt.cm.Vega20b(np.linspace(0,1,len(plots))))
    
    if person_selection_dict is not None:
        cnt = 0
        for p in pltList:
            c = colors[cnt]
            cnt += 1
           
            s,e = person_selection_dict[p[0]]
            cnts = [cnt for i in range(s,e+1)]
            ax2.plot(list(range(s,e+1)),cnts,c=c,**kwargs_plot)
  
def getCountsOfPersons(ma):
    persons = list(ma.keys())
    personCount={}
    personMaxCount={}
    import numpy as np
    import matplotlib.patches as mpatches
    for person in persons:
        cnt  = personCount.get(person,0)
        maxcnt = personMaxCount.get(person,0)
        for x in ma[person].values(): #hole alle rankings

                if x > 1:
                    cnt+=1
                if x >18: #top2:
                    #print(x)
                    maxcnt+=1

        personCount[person]=cnt
        personMaxCount[person]=maxcnt
    
    return personCount,personMaxCount
import pickle

def calculatePosition(graph,yr,storage_id,pickle_file=None,delete=False,intervall=1):
    pos = None
    poss={}
    
    if not delete:
            poss =  GraphCache().graphsStore.get("%s__%s_poss"%(intervall,storage_id),None)   
            
            if poss is None and pickle_file is not None:
                try:
                    poss=pickle.load(open(pickle_file,"rb"))
                except FileNotFoundError:
                    poss = {}
                    pos=None
            
            try:
                return poss[yr]  
            except KeyError:
                pos = None
    
    pos = graph.layout_graphopt(spring_constant=2,niter=1000)
    pos_x =[x[0] for x in pos]
    pos_y =[x[1] for x in pos]
    pos={"x":pos_x,"y":pos_y}
    logger.info("Create position for %s"%yr)    
    
    poss[yr]=pos
    
    GraphCache().graphsStore["%s__%s_poss"%(intervall,storage_id)]=poss
    
    if pickle_file is not None:
        logger.info("Writing to  %s"%pickle_file)
        pickle.dump(poss,open(pickle_file,"wb"))     
    return pos
 

def calculatePositions(graphs,storage_id,pickle_file=None,delete=False):
        """berechnet Positionen der Knoten für alle Graphen in graphs und speichert die Ergebnisse 
        in GraphCache
        @param graphs dict mit year->graph
        @param storage_id
        @returns dict mit dict[year]["x"] = liste der x-koordinaten der Knoten,
                    dict mit dict[year]["xy] = liste der y-koordinaten der Knoten.
        """
        poss=None
        
        
        
        if not delete:
            poss =  GraphCache().graphsStore.get("%s_poss"%storage_id,None)   
            
            if poss is None and pickle_file is not None:
                try:
                    poss=pickle.load(open(pickle_file,"rb"))
                except FileNotFoundError:
                    poss = None
                    
       
        if poss is not None and len(poss.keys()) == len (graphs.keys()):
            return poss
        
        poss={}
        
        for k,gr in graphs.items():
            #pos = gr.layout_fruchterman_reingold()
            pos = gr.layout_graphopt(spring_constant=2,niter=1000)
            pos_x =[x[0] for x in pos]
            pos_y =[x[1] for x in pos]
            pos={"x":pos_x,"y":pos_y}
            logger.info("Create position for %s"%k)
            poss[k]=pos
            
        GraphCache().graphsStore["%s_poss"%storage_id]=poss
        
        if pickle_file is not None:
            logger.info("Writing to  %s"%pickle_file)
            pickle.dump(poss,open(pickle_file,"wb"))     
        return poss

 
   
def loadGraphFromDV(content):
         
        uu = uuid.uuid4()
        urn_file = uu.urn
        #TODO has to become tempfile
        
        with open("/tmp/%s.graphml"%urn_file,"wb") as outf:
            outf.write(content.read())
        gr_all = igraph.load(open("/tmp/%s.graphml"%urn_file,"rb"))
        os.remove("/tmp/%s.graphml"%urn_file)
        content.close()
        return gr_all
        
    
def drawNW(ng,pos=None):

    pylab.rcParams['figure.figsize'] = (15, 15)

    if pos is None:
        pos=networkx.random_layout(ng)
    #pos=networkx.spring_layout(ng) # positions for all nodes

    # nodes
    networkx.draw_networkx_nodes(ng,pos,
                           nodelist=[n for n in ng.nodes() if ng.node[n].get("type","")=="institution"],
                           node_color='r',
                           node_size=40,
                       alpha=0.8)
    networkx.draw_networkx_nodes(ng,pos,
                           nodelist=[n for n in ng.nodes() if ng.node[n].get("type","")=="person"],
                           node_color='b',
                           node_size=40,
                       alpha=0.8)

    # edges
    networkx.draw_networkx_edges(ng,pos,width=1.0,alpha=0.5)
    networkx.draw_networkx_edges(ng,pos)
    #                       edgelist=[(0,1),(1,2),(2,3),(3,0)],
    #                       width=8,alpha=0.5,edge_color='r')
    plt.axis('off')
    #plt.show()




