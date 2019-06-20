from gherkan.utils.dictionaryMapper import DictionaryMapper
from gherkan.utils.dicts import sectionDict
import re
import unittest


class TestDictionaryMapper(unittest.TestCase):

    def setUp(self):
        flatText = u'# language: cs\n\n\n\npozadavek: robot n1\n\n  dil 2 je uchopen robotem n1 a na dil je naneseno lepidlo. v okmziiku, kdy je pripraven dil 1a nebo 1b je dil 2 prilepen k dilu 1. robot odpoji gripper a pripoji svarecku. nasledne k sobe svari dily 2 a 1a/b. po dokonceni svarovani robot odpoji svarecku.\n\n\n\nkontext:\n\n  pokud linkaon == 1\n\n\n\nscenar: zvednuti dilu\n\n  pokud part2ontable == 1 && (robotn1programnumber == 0 || robotn1programnumber == 1 || robotn1programended)\n\n  kdyz  tableathome\n\n  pak   robotn1programnumber == 1 && edge(robotn1programstart, 1)\n\n\n\nscenar: naneseni lepidla\n\n  kdyz  robotn1programnumber == 1 && edge(robotn1programended, 1)\n\n  pak   robotn1programnumber == 2 && edge(robotn1programstart, 1)\n\n\n\nscenar: slepeni dilu\n\n  pokud part1aontable == 1 || part1bontable == 1\n\n  kdyz  tableatfwd == 1\n\n  a     robotn1programnumber == 2 && edge(robotn1programended, 1)\n\n  pak   robotn1programnumber == 3 && edge(robotn1programstart, 1)\n\n\n\nscenar: vymena gripperu za svarecku\n\n  kdyz  robotn1programnumber == 3 && edge(robotn1programended, 1)\n\n  pak   robotn1programnumber == 4 && edge(robotn1programstart, 1)\n\n\n\nscenar: svareni produktu\n\n  kdyz  robotn1programnumber == 4 && edge(robotn1programended, 1)\n\n  pak   robotn1programnumber == 5 && edge(robotn1programstart, 1)\n\n\n\nscenar: vymena svarecky za gripper\n\n  kdyz  robotn1programnumber == 7 && edge(robotn1programended, 1)\n\n  pak   robotn1programnumber == 6 && edge(robotn1programstart, 1)'
        self.candidates = re.findall(r"\n\s*(\w*)", flatText, flags=re.MULTILINE)
        self.correctSections = ['description', '', 'context', 'while', 'scenario', 'while', 'if', 'then', 'scenario', 'if', 'then', 'scenario', 'while', 'if', 'and', 'then', 'scenario', 'if', 'then', 'scenario', 'if', 'then', 'scenario', 'if', 'then']
        self.correctFilteredSections = list(filter(lambda ix: ix[1], enumerate(self.correctSections)))
        self.dm = DictionaryMapper(sectionDict)

    @unittest.skip("Look-up dictionary testing not implemented for the Dictionary Mapper!")
    def test_lookup(self):
        self.assertTrue(False)
        # TODO
        # self.assertDictEqual(self.dm.lookup,
        #                      {}
        #                      )

    def test_map(self):
        self.assertListEqual(self.dm.map(self.candidates), self.correctSections)

    def test_filter(self):
        self.assertListEqual(self.dm.filter(self.candidates), self.correctFilteredSections)
