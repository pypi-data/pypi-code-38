from unittest import TestCase

from network_extensions import igraphx
from network_extensions.igraphx import multilayer
from network_extensions.igraphx.multilayer import MultiLayerGraph

import logging
logging.basicConfig(level = logging.DEBUG)

class TestMultiLayerGraph(TestCase):
    def test_writeGraphsToFile(self):
        ml2 = multilayer.MultiLayerGraph.load("data/co_author.pickle")
        with open("data/out/testout.tgz", "wb") as outf:
            ml2.writeGraphsToFile(outf)
        # self.pass()


    def test_simulate(self):
        ma = MultiLayerGraph.load("data/co_author.pickle")

        sims = ma.simulate(iterations=2)

        import pickle
        with open("data/out/sims.pickle", "wb") as outf:
            pickle.dump(sims, outf)

    def test_load(self):
        bip = MultiLayerGraph.BiPartiteGraph.load("data/person_nationality.graphml")

    def test_load_fmt(self):
        bip = MultiLayerGraph.BiPartiteGraph.load("data/person_nationality.graphml",format="graphml")



    def test_filter__es_ynw(self):
        test_title = "GRAVITATIONAL-SCALAR FIELD COUPLING"
        pt = "data/co-author-social_years_simplified_3.tgz"
        with open(pt, "rb") as outf:
            ynw_load = igraphx.loadGraphsFromFile(outf)

        ynw = multilayer.MultiLayerGraph.YearNetwork()
        ynw.update(ynw_load)
        transform = {"name": "title",
                     "func": str,
                     "default": ""}
        ynw = ynw.filter_es(title=test_title, transform=[transform])

        titles = []
        for y, gr in ynw.items():
            for i in gr.vs["inv"]:
                if test_title == i:
                    titles.append(i)

            self.assertEqual(len(titles), 0, "%s should NOT be in title anymore in year %s!" % (";".join(titles), y))

        with open("/tmp/ynws.tgz", "wb") as outf:
            igraphx.writeGraphsToFile(ynw, outf)

    def test_filter_ynw(self):
        pt = "data/co-author-social_years_simplified_3.tgz"
        with open(pt, "rb") as outf:
            ynw_load = igraphx.loadGraphsFromFile(outf)

        ynw = multilayer.MultiLayerGraph.YearNetwork()
        ynw.update(ynw_load)
        transform ={"name":"inv",
                    "func": int,
                    "default": 0}
        ynw = ynw.filter_vs(inv_lt=2,transform=[transform])

        insts = []
        for y,gr in ynw.items():
                for i in gr.vs["inv"]:
                    if i < 2:
                        insts.append(i)

                self.assertEqual(len(insts), 0, "%s should NOT be in inv anymore in year %s!" % (";".join(insts),y))

        with open("/tmp/ynws.tgz", "wb") as outf:
            igraphx.writeGraphsToFile(ynw,outf)

    def test_filter_es(self):
        ma = MultiLayerGraph.load("data/co_author.pickle")
        # print(ma.multi_layer.vs["label"])

        name = "institution_University"
        ma2 = ma.filter_es(name=name)

        insts = []
        for i in ma2.multi_layer.es["title"]:
            if i == name:
                insts.append(i)

        self.assertEqual(len(insts), 0, "%s should NOT be in the label anymore!" % ";".join(insts))
        with open("/tmp/out.tgz", "wb") as outf:
            ma2.writeGraphsToFile(outf)

    def test_filter_edge_by_vertices_ynw(self):
        pt = "data/co-author-social_years_simplified_3.tgz"
        with open(pt, "rb") as outf:
            ynw_load = igraphx.loadGraphsFromFile(outf)

        ynw = multilayer.MultiLayerGraph.YearNetwork()
        ynw.update(ynw_load)

        ynw = ynw.filter_edge_by_vertices("MISNER Charles W.","MATZNER Richard A.")

    def test_filter_edge_by_vertices(self):
        ma = MultiLayerGraph.load("data/co_author.pickle")

        ma2 = ma.filter_edge_by_vertices("USHAKOV Evgeny Alekseevich", "MINKEVICH Albert Vitoldovich")
        ma2 = ma2.filter_edge_by_vertices("MINKEVICH Albert Vitoldovich", "USHAKOV Evgeny Alekseevich")
        with open("/tmp/out.tgz", "wb") as outf:
            ma2.writeGraphsToFile(outf)
        with open("/tmp/in.tgz", "wb") as outf:
            ma.writeGraphsToFile(outf)

    def test_filter(self):
        ma = MultiLayerGraph.load("data/co_author.pickle")
        #print(ma.multi_layer.vs["label"])
        ma2 = ma.filter_vs(label_in = ['ADAM Madge Gertrude', 'AGNESE A. (A. G.)', 'AICHELBURG Peter C.'])

        insts = []
        for i in ma2.multi_layer.vs["label"]:
            if i in ['ADAM Madge Gertrude', 'AGNESE A. (A. G.)', 'AICHELBURG Peter C.']:
                insts.append(i)

        self.assertEqual(len(insts),0,"%s should NOT be in the label anymore!" %";".join(insts))
        with open("/tmp/out.tgz","wb") as outf:
            ma2.writeGraphsToFile(outf)

    def test_filter_transform(self):
        transform = [{"name": "inv",
                      "func": int,
                      "default": 0}]

        ma = MultiLayerGraph.load("data/co_author.pickle")
        # print(ma.multi_layer.vs["label"])
        ma2 = ma.filter_vs(inv_lt=2, transform = transform)

        insts = []
        for i in ma2.multi_layer.vs["inv"]:
            if i < 2:
                insts.append(i)

        self.assertEqual(len(insts), 0, "%s should NOT be in inv anymore!" % ";".join(insts))
        with open("/tmp/out2.tgz", "wb") as outf:
            ma2.writeGraphsToFile(outf)

    def test_update_multilayer(self):
        ma = MultiLayerGraph.load("data/co_author.pickle")
        ma.update_multilayer()


    def test_get_simplified_multi_layer_ynws(self):
        ma = MultiLayerGraph.load("data/co_author.pickle")

        simpl = ma.get_simplified_multi_layer_ynws(1)

        self.assertEqual(len(simpl),6,"there should be 6 different simplifications in %s"%simpl.keys()) #shoudld contain six networks

        for i,ynws in simpl.items():
            self.assertEqual(len(ynws),len(ma.ynws))
            for y,ynw in ynws.items():

                self.assertEqual(len(ynw.vs),len(ma.ynws[y].multi_layer.vs),"should be same amount of nodes")

                if i == "orginal":
                    self.assertEqual(len(ynw.es), len(ma.ynws[y].multi_layer.es), "should be same amount of edges")
                else:
                    ynw.save("/tmp/test.graphml")
                    ma.ynws[y].multi_layer.save("/tmp/original.graphml")
                    print(i,len(ynw.es), len(ma.ynws[y].multi_layer.es))
                    self.assertLessEqual(len(ynw.es), len(ma.ynws[y].multi_layer.es), "should %s be same amount or less of edges"%i)

        simpl = ma.get_simplified_multi_layer_ynws(-100)
        comp = ma.merged_ynws[-100].ynws
        self.assertEqual(len(simpl), 6,
                         "there should be 6 different simplifications in %s" % simpl.keys())  # shoudld contain six networks

        for i, ynws in simpl.items():
            ynw.save("/tmp/test.graphml")
            ma.ynws[y].multi_layer.save("/tmp/original.graphml")
            self.assertEqual(len(ynws), len(ma.ynws))
            for y, ynw in ynws.items():

                self.assertEqual(len(ynw.vs), len(comp[y].multi_layer.vs), "should %s (%s) be same amount of nodes!" %(i,y))

                if i == "original":
                    self.assertEqual(len(ynw.es), len(comp[y].multi_layer.es), "should be same amount of edges")
                else:

                    print(i, len(ynw.es), len(comp[y].multi_layer.es))
                    self.assertLessEqual(len(ynw.es), len(comp[y].multi_layer.es),
                                         "should %s be same amount or less of edges" % i)
