from unittest import TestCase

from network_extensions.igraphx.multilayer import MultiLayerGraph, saveSimGraphs


class TestSaveSimGraphs(TestCase):
    #TODO write a better test!
    def test_saveSimGraphs(self):
        import pickle
        ma = MultiLayerGraph.load("data/co_author.pickle")

        sims = ma.simulate(iterations=2)

        import pickle
        with open("/tmp/sims.pickle", "wb") as outf:
            pickle.dump(sims, outf)

        with open("/tmp/out.tgz", "wb") as outf:
            saveSimGraphs(sims, outf)
