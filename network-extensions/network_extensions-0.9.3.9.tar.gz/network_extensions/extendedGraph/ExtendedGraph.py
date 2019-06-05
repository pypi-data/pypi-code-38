import uuid
from multiprocessing.pool import Pool

#from memory_profiler import profile
import igraph
from collections import defaultdict, OrderedDict

import pickle

import os
from tqdm import tqdm
from time import time

from network_extensions.extendedGraph.RedisDataTypes import RedisBase, RedisDictList, RList, CACHE, REDIS_MODE
from network_extensions.igraphx import getA, projectBipartiteParallel

import logging

class ExtendedGraph(igraph.Graph):
    """Extended Graph keeps attritebutes of nodes in separate list"""
    def __init__(self,**kwargs):
        igraph.Graph.__init__(self,**kwargs)
        self.initialize()

    def initialize(self):
        self.edgeAttrs = defaultdict(list)
        self.edgeListLong = []
        self.edgeList = set()
        self.multiEdges = defaultdict(list) # contain a list of edges parallel to the starting one
        self.edgeAttrNames = set()
        self.edgesByStartYear = None
        self.startYearEdgeAttribute = None  # contains later the attribute name  for start-year at the edges
        self.newEdges = []  # list for edges not added to dictionaries

        self.edges_changed = False




    def checkEdges(self):
        if self.edges_changed:
            print("Warning: edges have change - value might be incorrect")

        return self.edges_changed

    def set_edgeAttrsDict(self,edgelist=None, onlyNew = False):
        """ creates from the long list of edges  lists of attributes attached to the edges"""
        if edgelist is None:
            if onlyNew:
                edgelist = self.newEdges
                self.edgeListLong += edgelist
            else:
                edgelist = self.edgeListLong # recreate everything
                self.edgeAttrs = defaultdict(list)
                self.edgeAttrNames = set()
            self.newEdges = []


        self.edges_changed = True
        print("creating: attrsdict")
        for s,e,attrs in tqdm(edgelist):
            self.edgeAttrs[(s,e)].append(attrs) #jedes kante bekommt eine liste von attributen
            self.edgeAttrNames.update(attrs.keys()) # merke alle attributnamen
            self.edgeList.add((s,e))



    def get_edgeAttrNames(self):

        if len(self.es) == 0:
            return []
        
        assert len(self.edgeAttrs) > 0, "Edge Attrs not set, run  set_edgeAttrsDict first"

        self.checkEdges()
        return self.edgeAttrNames


    def add_edge(self, source, target, **kwds):
        #fuegt eine kante der liste hinzu

        self.edgeListLong.append((source,target,kwds))
        self.newEdges.append((source,target,kwds))


        self.edges_changed =  True
        eid = self.ecount()

        igraph.Graph.add_edges(self, [(source, target)])
        if (source,target) in self.self.edgeAttrs: #gibt schon einen eintrag mit attributen
            self.multiEdges[(source,target)].append(eid) #multiedge

        self.edgeList.add((source, target))

        if len(kwds) > 0:
            self.edgeAttrs[(source, target)].append(kwds)
            self.edgeAttrNames.update(kwds.keys())

    def add_edges(self,el=None,v_attr_name=None):
        logging.debug("add_edges")
        el2 = []
        if el is None:
            el = self.edgeList
        logging.debug("add: %s"%len(el))
        for e in tqdm(el):
            try:
                source, target, kwargs = e
                if v_attr_name is not None:
                    source = self.vs.select(**{v_attr_name:source})[0].index
                    target = self.vs.select(**{v_attr_name:target})[0].index
                self.add_edge(source,target,kwargs)

            except ValueError: # a bit of hack if only two in el dann use addEdges from super
                source, target = e
                if v_attr_name is None:
                    el2.append((source, target))
                else:
                    source,target = e
                    source = self.vs.select(**{v_attr_name: source})[0].index
                    target = self.vs.select(**{v_attr_name: target})[0].index

                    el2.append((source,target))
        self.edgeList.update(el2)
        igraph.Graph.add_edges(self,el2)

    def edgeAttrsDictToEdgeAttr(self,attr=None,v_attr_name=None):
        assert len(self.edgeAttrs) == len(self.edgeList), "Edge Attrs not set, run  set_edgeAttrsDict first"
        if isinstance(attr,str):
            try:
                newAttrs_first = [self.edgeAttrs[ed][0][attr] for ed in self.edgeList]
                #self.es[attr] =[self.edgeAttrs[ed][0][attr] for ed in self.edgeList] # zunächst jeweils des ersten Eintrag aus dem Anttribute dictionary.
            except KeyError:
                print("warning: key %s doesn't exist!"%attr)
                self.es[attr] = ""

            print("multidict")
            eid = self.ecount() #keep counter
            newEdges = []
            newAttrs = []
            #jetzt gehen wir noch durch die Multieges
            eid = self.ecount() # current edgeid
            for ed in tqdm(self.edgeList):
                cnt = 0
                start_time = time()
                for attrs in self.edgeAttrs[ed][1:]: #gehe durch alle attribute die an der Katen hängen, da eine Multi-edge ist die Liste länger als 1
                    try:
                        current_edge= self.multiEdges[ed][cnt]
                        self.es[current_edge][attr] = attrs[attr]

                    except IndexError: #multiedge doesn't exist

                        #igraph.Graph.add_edges(self,[(ed[0],ed[1])])

                        if v_attr_name is not None:
                            source = self.vs.select(**{v_attr_name: ed[0]})[0]
                            target = self.vs.select(**{v_attr_name: ed[1]})[0]
                            newEdges.append((source,target))
                        else:
                            newEdges.append(ed)

                        self.multiEdges[ed].append(eid) # fueg neue eid hinzu

                        newAttrs.append(attrs[attr])
                        eid  += 1
                    cnt+=1
                #print(time()-start_time)
            #old_attrs = self.es[attr]
            igraph.Graph.add_edges(self, newEdges) #jetzt lege die Kanten wirklich an
            all_attrs = newAttrs_first + newAttrs
            for i in range(0,len(all_attrs)):
                self.es[i][attr] = all_attrs[i]
            #self.es[attr] = newAttrs_first + newAttrs # und fueger deren attribute hinzu

        elif attr is None:
            for a in self.edgeAttrNames:
                self.edgeAttrsDictToEdgeAttr(a,v_attr_name=v_attr_name)
        else:
            for a in attr:
                self.edgeAttrsDictToEdgeAttr(a)


    def getEdgesByStartYear(self):
        return self.edgesByStartYear

    def getEdgesByStartYearItems(self):
        return self.edgesByStartYear.items()

    def initEdgesByStartYear(self):
        self.edgesByStartYear = defaultdict(dict)

    def appendEdgesByStartYear(self,startYear,endYear,data):
        try:
            self.edgesByStartYear[startYear][endYear].append(data)
        except KeyError:
            self.edgesByStartYear[startYear][endYear] = [data]

    def orderEdgesByStartYear(self):
        self.edgesByStartYear = OrderedDict(sorted(self.edgesByStartYear.items(), key=lambda t: t[0]))
        for y, grs in self.edgesByStartYear.items():
            self.edgesByStartYear[y] = OrderedDict(sorted(grs.items(), key=lambda t: t[0]))

    def getEdges_per_start_yearValuesLen(self,y):
        for v in self.edgesByStartYear[y].values():
            yield len(v)

    def getEdges_per_start_yearValues(self,y):
        for v in self.edgesByStartYear[y].values():
            yield v

    def getEdges_per_start_yearEndYear(self,sy,ey):
        return self.edgesByStartYear[sy][ey]

    def get_edges_endyear(self,edges_endyear):
        return edges_endyear.items()

    def createYearNetworksParallel(self, startyear, endyear, startyear_edge_attr=None,endyear_edge_attr=None, worker=6, **kwargs):
        print("Starting creating year networks with %s workers."%worker)

        # first I have to check if the attributes exist
        assert startyear_edge_attr in self.edgeAttrNames, "Edge Attribute %s for start doesn't exist, only know: %s"%(startyear_edge_attr,self.edgeAttrNames)
        assert endyear_edge_attr in self.edgeAttrNames, "Edge Attribute %s for end doesn't exist"%endyear_edge_attr

        # check if the start_year has already exists
        if self.getEdgesByStartYear() is None or self.startYearEdgeAttribute != startyear_edge_attr or self.endYearEdgeAttribute != endyear_edge_attr:
            try:
                self.setMode(kwargs.get("mode"))
                print("MODE: %s"%kwargs.get("mode"))
            except AttributeError:
                pass  # not implemented
            self.initEdgesByStartYear()
            self.startYearEdgeAttribute = startyear_edge_attr  # keep this safe
            self.endYearEdgeAttribute = endyear_edge_attr  # keep this safe


            print("have to create start_year_edge hash first")

            for edge, attrs in tqdm(self.edgeAttrs.items()):

                for attr in attrs:
                    try:
                        self.appendEdgesByStartYear(int(attr[startyear_edge_attr]),int(attr[startyear_edge_attr]),(edge,attr))
                    except ValueError:
                        print("either %s startyear or %s endyear is not an integer it is %s %s!" % (
                        startyear_edge_attr, endyear_edge_attr,attr[startyear_edge_attr],attr[startyear_edge_attr]))

            self.orderEdgesByStartYear()
            try:
                print("SAVE CACHES")
                self.saveCaches()
                self.setMode(REDIS_MODE)
            except AttributeError:
                pass #not implemented


        years = range(startyear, endyear)

        kwargs["startyear_edge_attr"] = startyear_edge_attr
        kwargs["endyear_edge_attr"] = endyear_edge_attr

        #ng_data = ng.write_picklez("/tmp/gr.picklez")
        data = []
        node_attrs = [n.attributes() for n in self.vs]

        fn = uuid.uuid4().urn
        with open("/tmp/%s_nodes"%fn,"wb") as outf:
            pickle.dump(node_attrs,outf)

        #with open("/tmp/%s_edges" % fn, "wb") as outf:
        #    pickle.dump(self.edgesByStartYear, outf)

        ## lets try to create chunks depending on the number of edges per year
        no_of_edges_per_year = {}

        for y,z in self.getEdgesByStartYearItems():
            if y in years:
                no_of_edges_per_year[y] = sum(x for x in self.getEdges_per_start_yearValuesLen(y))

        number_of_edges = sum(no_of_edges_per_year.values())
        print ("I have to distribute the generation of %s edges more ore less equally over the years"%number_of_edges)

        edges_per_chunk = int(number_of_edges / worker) + 1 # allways round up
        print("This means %s edges per chunk with %s workers" % (edges_per_chunk,worker))

        current_no_of_edges = 0
        current_startyear = startyear

        for year in years:
            if year not in no_of_edges_per_year:
                print("year %s has no edges starting there"%year)
                no_of_eadges_year = 0
            else:
                current_no_of_edges += no_of_edges_per_year[year]
                no_of_eadges_year = no_of_edges_per_year[year]

            print("%s, %s : %s"%(year,current_no_of_edges,edges_per_chunk))
            if current_no_of_edges > edges_per_chunk:

                if (current_no_of_edges -  no_of_eadges_year)/(current_no_of_edges +  no_of_eadges_year) < 0.15: #only a bit over the limit
                    data.append([current_startyear, year+1, kwargs, fn, None]) # take this year to
                    print("%s - %s : %s edges" % (current_startyear, year+1, current_no_of_edges))
                    current_no_of_edges = 0
                    current_startyear = year+1
                else:
                    data.append([current_startyear,year,kwargs,fn,None])
                    print("%s - %s : %s edges" % (current_startyear,year,current_no_of_edges -  no_of_eadges_year))
                    current_startyear = year
                    current_no_of_edges = no_of_eadges_year

        print("%s - %s : %s edges (rest)" % (current_startyear, year +1, current_no_of_edges))
        data.append([current_startyear, year+1, kwargs, fn, None]) # all the rest
        data2 = []
        for s,e,k,fn,n in data:
            #create portions of edges relevant
            if isinstance(self,RedisBase):
                pw = RedisDictList(keyFunc=int)
            else:
                pw = defaultdict(dict)
            for start_year in range(s,e+1):
                for y,edges_endyear in self.getEdgesByStartYearItems():
                    if y > start_year:
                        continue

                    for end_year,edges in self.get_edges_endyear(edges_endyear):
                        if int(end_year) < start_year:
                            continue

                        pw[y][end_year]= edges




            fn2 = uuid.uuid4().urn
            if isinstance(pw,RedisDictList):
                with open("/tmp/%s_edges" % fn2, "wb") as inf:
                    pw.dump(inf)
                    type = "redis"
            else:
                pw = OrderedDict(sorted(pw.items(), key=lambda t: t[0]))
                with open("/tmp/%s_edges" % fn2, "wb") as inf:
                    pickle.dump(pw,inf)
                    type = "pickle"
            data2.append([s, e, k, fn, fn2,type])

       # for y in chunks(years, max(int(len(years) / worker),1)):
       #    data.append([y[0], y[-1] + 1 , kwargs,fn])
        #print(data)
        #print([(x[0],x[1]) for x in data2])

        with Pool(len(data2)) as p:
            ret = p.map(self.__class__.createYearNetworksProcess, data2)

        retdict = ret[0]
        for r in ret[1:]:
            retdict.update(r)
        return retdict

    @staticmethod
    def createYearNetworksProcess(data):

        #ng = igraph.read("/tmp/gr.picklez")
        fn = data[3]
        with open("/tmp/%s_nodes" % fn, "rb") as inf:
            nl = pickle.load(inf)

        type = data[5]
        with open("/tmp/%s_edges" % data[4], "rb") as inf:
            if type == "redis":
                ey = RedisDictList.load(inf,keyFunc=int)
            else:
                ey = pickle.load(inf)

        return ExtendedGraph.createYearNetworks(nl, data[0],data[1], edgesByStartYear=ey,**data[2])

    @classmethod
    def createYearNetworks(cls,self, startyear, endyear, typ=None,
                           startYear_default=1880, endYear_default=2010, filter_degree_0=True,
                           startyear_attr="startYear", endyear_attr="endYear",
                           startyear_edge_attr=None, endyear_edge_attr=None,
                           include_nodes_without_date=False,
                           simplify=False,
                           combine_edges=None,
                           edgesByStartYear=None,
                           only_edge_list=False,
                           DEBUG=True,
                           mode = REDIS_MODE):
        ynw = {}
        createdNodes = 0
        createdEdges = 0
        from time import time
        start_time = time()
        if issubclass(type(self),ExtendedGraph) or isinstance(self,ExtendedGraph): #
            assert edgesByStartYear is None, "parameter edgesByStartYear should be set if method called as instance method"
            ng_an = self.copy()

            #first I have to check if the attributes exist
            assert startyear_edge_attr in self.edgeAttrNames, "Edge Attribute for start doesn't exist"
            assert endyear_edge_attr in self.edgeAttrNames, "Edge Attribute for end doesn't exist"
            try:
                self.setMode(mode)
            except AttributeError: #not implemented
                pass

            #check if the start_year has already exists
            if self.getEdgesByStartYear() is None or self.startYearEdgeAttribute != startyear_edge_attr or self.endYearEdgeAttribute !=endyear_edge_attr:
                #self.edgesByStartYear = defaultdict(dict)
                self.initEdgesByStartYear()
                self.startYearEdgeAttribute = startyear_edge_attr # keep this safe
                self.endYearEdgeAttribute = endyear_edge_attr  # keep this safe

                print("have to create start_year_edge hash first")
                #print(type(self.getEdgesByStartYear()))
                for edge,attrs in tqdm(self.edgeAttrs.items()):
                    for attr in attrs:
                        try:
                            self.appendEdgesByStartYear(int(attr[startyear_edge_attr]),
                                                        int(attr[endyear_edge_attr]), (edge, attr))
                        except ValueError:
                            print("either %s startyear or %s endyear is not an integer!" % (
                                startyear_edge_attr, endyear_edge_attr))

                self.orderEdgesByStartYear()

            edgesByStartYear = self.getEdgesByStartYear()
            try:
                self.saveCaches()
            except AttributeError: #not implemented
                pass
        else:
            assert  edgesByStartYear is not None, "edgesByStartYear must be set"
            ng_an = igraph.Graph()
            for attr in self:
                ng_an.add_vertex(**attr)

        iter = tqdm(range(startyear, endyear))

        if DEBUG:
            fn = uuid.uuid4().urn
            outf = open("/tmp/%s.csv"%fn, "w")

        for y in iter:
            iter_start_time = time()
            # print(y)
            nw = igraph.Graph(directed=True)
            edgelist = []
            # erst alle nodes im zeitraum
            if issubclass(type(edgesByStartYear),RedisBase):
                edgelist = RList()
            for node in ng_an.vs:
                if typ is not None and node["type"] != typ:
                    ng_an.delete_vertices([node])
                    continue
                # print (ng_an.node[node]["type"])
                try:
                    sy = node[startyear_attr]
                    if sy is None:
                        sy = startYear_default
                except KeyError:
                    sy = startYear_default

                try:
                    ey = node[endyear_attr]
                    if ey is None:
                        ey = endYear_default
                except KeyError:
                    ey = endYear_default

                if str(sy).lower() == "no" or str(sy).lower() == "" or str(sy).lower() == "none":
                    # dont Include him/she in the YearNetWork
                    if not include_nodes_without_date:
                        continue
                    else:
                        sy = startYear_default

                if str(ey).lower() == "no" or str(ey).strip() == "" or str(ey).lower() == "none":
                    ey = endYear_default

                # print(sy,ey)
                if y in range(int(sy), int(ey) + 1):
                    attrs = node.attributes()
                    nw.add_vertex(old_id=node.index, **node.attributes())

            # jetzt alle Kanten:

            for sy,edges_by_end_year in edgesByStartYear.items():

                if sy > y:
                    continue # start year not relevant anymore

                if isinstance(self,list):
                    iter_end = edges_by_end_year.items()
                else:
                    iter_end = self.get_edges_endyear(edges_by_end_year)

                for ey,edges in iter_end:
                    if ey < y:
                        continue

                    for g in edges:
                        e,attr = g

                        if only_edge_list:
                            edgelist.append((e[0], e[1], attr))
                        else:
                            nw.add_edge(e[0], e[1], **attr)


            if filter_degree_0:
                deln = nw.vs.select(_degree=0)
                nw.delete_vertices(deln)

            # print(y,len(nw.vs))
            if simplify:
                nw.simplify(multiple=True, loops=True, combine_edges=combine_edges)
            if only_edge_list:
                if isinstance(edgelist,RList):
                    ynw[y] = (nw, edgelist.key_int)
                    print( edgelist.key_int,len(edgelist))
                else:
                    ynw[y] = (nw,edgelist)
            else:
                ynw[y] = nw

            createdNodes +=  len(nw.vs)
            createdEdges += len(nw.es)


            if DEBUG:
                outf.write(("%s,%s,%s,%s,%s\n" % (time() - iter_start_time, y, y, len(nw.vs),len(nw.es))))


        time = time() - start_time
        if DEBUG:
            outf.write(("%s,%s,%s,%s,%s\n"%(time,startyear,endyear,createdNodes,createdEdges)))
            outf.close()

        return ynw

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
        logging.debug("get edge list long, mode %s"%self.mode)
        if len(self.edgeListLong) == 0:  # can happen if edgeList ist created directly e.g by loading from file
            for (s,e),attrs in tqdm(self.edgeAttrs.items()):
                for attr in attrs:
                    self.edgeListLong.append((s,e,attr))
        return self.edgeListLong

    @classmethod
    def load_extGraph(cls,folder):
        if not os.path.exists(folder):
            raise FileNotFoundError

        #gr = ExtendedGraph()
        gr  = cls.Read_GraphML(os.path.join(folder,"graph.graphml"))
        cls.initialize(gr)


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

        try:
            gr.setMode(CACHE)
        except:
            pass #not implemented
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
        """ siehe https://github.com/igraph/igraph/issues/876
        Erzeugt die Vereinigung zweier (gerichteter) Graphen über gemeinsame "v_attr_name".
        Kanten mit gleichen Attribute werden zusammengefasst. Zur Zeit wird ein eventuelles "weight"-Attribute
        herausgefilter.

        @param g_1 Graph 1
        @param g_2 Graph 2
        @param v_attr_name Name des Attributes, dass zur eindeutigen Identifikation der Knoten  benutzt werden kann.

        @returns vereinigten Graphen
        """
        assert len(set(g_1.vs[v_attr_name])) == len(g_1.vs[v_attr_name]), "Merging attribute must be unique"
        assert len(set(g_2.vs[v_attr_name])) == len(g_2.vs[v_attr_name]), "Merging attribute must be unique"

        v_attr_1 = g_1.vs[v_attr_name]
        v_attr_2 = g_2.vs[v_attr_name]

        #attrs = set(g_1.get_edgeAttrNames())
        #attrs.update(set(g_2.get_edgeAttrNames()))

        #lets first merge the nodes


        newGr = cls()

        newNodes = defaultdict(dict)
        #old_to_new_id = defaultdict(dict)
        #collect all nodes
        for g in [g_1,g_2]:
            print(id(g))
            for n in tqdm(g.vs):
                nid = n[v_attr_name]
                newNodes[nid].update(n.attributes())
                #old_to_new_id[n.index][id(g)]=nid


        #adding nodes to the newgraph


        for nid,vals in newNodes.items():

                if "name" in vals: ##has to be renamed
                    vals["name_safe"] = vals.pop("name")

                newGr.add_vertex(nid,**vals)
        print("H")

        nameSafe2Name = {x:y for x,y in zip(newGr.vs["name_safe"],newGr.vs["name"])}
        #now we create the edges list of the union for x,y in zip(newGr.vs["name_save"],newGr.vs["name"]

        for g in [g_1,g_2]:

            for s,e,attrs in tqdm(g.edgeListLong):
                #try:
                #    ns = old_to_new_id[s.index][id(g)]
                #    new_s = newGr.vs[ns].index
                #except KeyError:
                #    continue #not in one of the graphs
                #new_t = newGr.vs[old_to_new_id[s.index][id(g)]].index
                #print("add")


                newGr.edgeListLong.append((nameSafe2Name.get(s,s),nameSafe2Name.get(e,e),attrs))
                
        return newGr

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
                    g = ExtendedGraph.union(g, graphs[y], mergeattr)
                else:
                    print("ignore %s"%y)
                    pass  # ignore missing years

            if onlyNodesInYear is not None:  # loesche alle Knoten, die am Anfnge
                delNode = []
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
                    if not onlyNodesInYear in range(sy, ey + 1):
                        delNode.append(n)
                # print(y,delNode)
                g.delete_vertices(delNode)

            return g
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
