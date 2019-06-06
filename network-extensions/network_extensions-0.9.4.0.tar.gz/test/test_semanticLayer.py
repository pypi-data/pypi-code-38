from unittest import TestCase

from network_extensions.igraphx.semantic.semantic import SemanticLayer


class TestSemanticLayer(TestCase):
    def test_createYearNetworks(self):
        solr_url = "http://%s:%s@dw2.mpiwg-berlin.mpg.de:38983/solr/abstracts" % ("solr", "5!7DjpW6")

        cr = SemanticLayer(solr_url)
        cr.createYearNetworks(1930, 1932, max_number_terms= 20)

        for y, gr in cr.ynws.items():
            print(y, len(gr.es), len(gr.vs))

        self.assertGreater(len(cr.ynws), 0)

    def test_generateMultiLayer(self):
        solr_url = "http://%s:%s@dw2.mpiwg-berlin.mpg.de:38983/solr/abstracts" % ("solr", "5!7DjpW6")

        cr = SemanticLayer(solr_url)
        cr.createYearNetworks(1930, 1932, max_number_terms= 10)

        cr.generateMultiLayer()
