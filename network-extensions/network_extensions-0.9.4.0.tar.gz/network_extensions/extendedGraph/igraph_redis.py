from network_extensions.extendedGraph.ExtendedGraph import ExtendedGraph
from network_extensions.extendedGraph.RedisDataTypes import DynamicEdgeListLong, RedisDictList, RedisBase
import uuid


class ExtendedRedisGraph(ExtendedGraph,RedisBase):

    def __init__(self,**kwargs):
        ExtendedGraph.__init__(self,**kwargs)
        RedisBase.__init__(self)
        self.initialize()

    def initialize(self):
        RedisBase.__init__(self)
        ExtendedGraph.initialize(self)
        self.redis_uuid = uuid.uuid4().urn
        self.edgesByStartYear_set=False
        self.edgeListLong = DynamicEdgeListLong()

    def saveCaches(self):
        self.caches.saveCaches()

    def deleteCaches(self):
        self.caches.deleteCaches()

    def initEdgesByStartYear(self):
        self.edgesByStartYear = RedisDictList(keyFunc=int)

    def orderEdgesByStartYear(self):
        pass
        #self.edgesByStartYear = OrderedDict(sorted(self.edgesByStartYear.items(), key=lambda t: t[0]))
        #for y, grs in self.edgesByStartYear.items():
        #    self.edgesByStartYear[y] = OrderedDict(sorted(grs.items(), key=lambda t: t[0]))

    @staticmethod
    def createYearNetworksProcess(data):
        # ng = igraph.read("/tmp/gr.picklez")

        fn = data[3]
        with open("/tmp/%s_nodes" % fn, "rb") as inf:
            nl = pickle.load(inf)

        type = data[5]
        with open("/tmp/%s_edges" % data[4], "rb") as inf:
            if type == "redis":
                ey = RedisDictList.load(inf, keyFunc=int)
            else:
                ey = pickle.load(inf)

        return ExtendedRedisGraph.createYearNetworks(nl, data[0], data[1], edgesByStartYear=ey, **data[2])


if __name__ == "__main__":
        import pickle
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

        gr = ExtendedRedisGraph.getGraphFromEdgeAndNodeLists(edgeList=el,nodeDict=nd)
        gr.set_edgeAttrsDict(el)
        gr.edgeAttrsDictToEdgeAttr(None)
        print ("Now I have to save everything")
        gr.save_extGraph(("/tmp/extgt"))
        gr2 = ExtendedRedisGraph.load_extGraph("/tmp/extgt")

        assert len(gr.vs) == len(gr2.vs), "Nodes, Should be the same"
        assert len(gr.es) == len(gr2.es), "Edges, Should be the same"

        assert len(set(gr.vs["name"]) - set(gr.vs["name"])) == 0, "should be zero"

        assert len(gr.multiEdges) == len(gr2.multiEdges), "should be equal"
        assert len(gr.edgeAttrs)  == len(gr2.edgeAttrs), "should be equal"
        assert len(gr.edgeList) == len(gr2.edgeList), "should be equal"


        print("done")
        #print(gr.es["year"])

