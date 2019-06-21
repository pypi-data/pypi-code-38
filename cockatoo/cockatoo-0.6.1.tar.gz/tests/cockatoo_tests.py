from nose.tools import *
import os
import csv
from pinky.smiles import smilin
import cockatoo
from cockatoo import xtuition
from cockatoo.screen import Screen,Cocktail,Compound

class TestUtil:
    def setup(self):
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.csv_test_screen = "%s/../screens/csv/test-screens/salt-concentration.csv" % self.path
        self.test_cocktail = "%s/../data/C0160.json" % self.path
        self.ph_screen = "%s/../screens/json/test-screens/ph.json" % self.path
        self.salt_screen = "%s/../screens/json/test-screens/salt-concentration.json" % self.path
        self.conc_screen = "%s/../screens/json/test-screens/conc.json" % self.path
        self.peg_screen = "%s/../screens/json/test-screens/peg-mw.json" % self.path
        self.cation_screen = "%s/../screens/json/test-screens/cation.json" % self.path
        self.anion_screen = "%s/../screens/json/test-screens/anion.json" % self.path
        self.hwi_gen8 = "%s/../screens/json/hwi/hwi-gen8.json" % self.path
        self.hwi_gen8A = "%s/../screens/json/hwi/hwi-gen8A.json" % self.path

    def teardown(self):
        pass

    def test_basic(self):
        cp1 = Compound('sodium chloride', 1.0, 'M')
        c1 = Cocktail('c1')
        c1.add_compound(cp1)
        s = Screen('screen1')
        s.add_cocktail(c1)
        s.print_stats()

        assert len(s) == 1

    def test_smiles(self):
        with open('%s/../data/hwi-compounds.csv' % self.path) as fh:
            reader = csv.DictReader(fh, delimiter="\t")
            for row in reader:
                if len(row['smiles']) == 0: continue
                mol = smilin(row['smiles'])
                assert mol != None

    def test_parse_csv(self):
        s = cockatoo.screen.parse_csv('salt-con', self.csv_test_screen)
        s.print_stats()
        assert len(s) == 12

    def test_parse_cocktail(self):
        c = cockatoo.screen.parse_cocktail(self.test_cocktail)
        print(c)

    def test_parse_json(self):
        s = cockatoo.screen.load(self.salt_screen)
        s.print_stats()
        assert len(s) == 12
        s = cockatoo.screen.load(self.hwi_gen8)
        s.print_stats()
        assert len(s) == 1536

        for ck in s.cocktails:
            assert ck.ph is not None

    def test_molarity(self):
        s = cockatoo.screen.load(self.hwi_gen8)
        # v/v
        ck = s.cocktails[49]
        cp = ck.components[0]
        assert round(cp.molarity(),3) == 4.789
        # w/v
        ck = s.cocktails[231]
        cp = ck.components[1]
        assert round(cp.molarity(),3) == 0.032
        # M
        ck = s.cocktails[222]
        cp = ck.components[0]
        assert round(cp.molarity(),3) == 3.050

    def test_metric(self):
        w = [0,1]
        s = cockatoo.screen.load(self.salt_screen)
        print("\t".join(['i','j','score']))
        for i in range(0, len(s)):
            for j in range(0, len(s)):
                score = cockatoo.metric.distance(s.cocktails[i], s.cocktails[j], w)
                print("\t".join([str(i),str(j),str(score)]))

    def test_xtuition(self):
        if 'XTUITION_TOKEN' in os.environ:
            s = xtuition.fetch_screen(6)
            print(s)
            c = xtuition.fetch_cocktail(7688)
            print(c)
            c = xtuition.fetch_compound(45)
            print(c)
            c = xtuition.fetch_compound_by_name('sodium bromide')
            print(c)
