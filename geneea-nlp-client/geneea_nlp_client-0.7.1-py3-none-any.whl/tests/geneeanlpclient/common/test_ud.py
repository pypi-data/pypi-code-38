from unittest import TestCase

import geneeanlpclient.common.ud as ud


class TestUd(TestCase):

    def test_Pos(self):
        self.assertEqual(ud.UPos.ADJ, ud.UPos.fromStr('ADJ'))
        self.assertEqual(ud.UPos.X, ud.UPos.fromStr('unknown'))

    def test_Dep(self):
        self.assertEqual(ud.UDep.DOBJ, ud.UDep.fromStr('DOBJ'))
        self.assertEqual(ud.UDep.DEP, ud.UDep.fromStr('unknown'))
