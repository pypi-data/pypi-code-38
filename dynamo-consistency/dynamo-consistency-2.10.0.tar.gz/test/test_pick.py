#! /usr/bin/env python

# This is to test regular expressions
# Also, we want to generate a regular expression that avoids picking RAL

import unittest
import base
import os

from dynamo_consistency import backend

backend.siteinfo.site_list = lambda: [
    "T1_DE_KIT_Disk", "T1_ES_PIC_Disk", "T1_FR_CCIN2P3_Disk", "T1_IT_CNAF_Disk", "T1_RU_JINR_Disk", "T1_UK_RAL_Disk", "T1_US_FNAL_Disk",
    "T2_AT_Vienna", "T2_BE_IIHE", "T2_BE_UCL", "T2_BR_SPRACE", "T2_BR_UERJ", "T2_CH_CERN", "T2_CH_CSCS", "T2_CN_Beijing", "T2_DE_DESY",
    "T2_DE_RWTH", "T2_EE_Estonia", "T2_ES_CIEMAT", "T2_ES_IFCA", "T2_FI_HIP", "T2_FR_CCIN2P3", "T2_FR_GRIF_IRFU", "T2_FR_GRIF_LLR", "T2_FR_IPHC",
    "T2_GR_Ioannina", "T2_HU_Budapest", "T2_IN_TIFR", "T2_IT_Bari", "T2_IT_Legnaro", "T2_IT_Pisa", "T2_IT_Rome", "T2_KR_KISTI", "T2_KR_KNU",
    "T2_MY_UPM_BIRUNI", "T2_PK_NCP", "T2_PL_Swierk", "T2_PL_Warsaw", "T2_PT_NCG_Lisbon", "T2_RU_IHEP", "T2_RU_INR", "T2_RU_ITEP", "T2_RU_JINR",
    "T2_RU_PNPI", "T2_RU_SINP", "T2_TH_CUNSTDA", "T2_TR_METU", "T2_TW_NCHC", "T2_UA_KIPT", "T2_UK_London_Brunel", "T2_UK_London_IC", "T2_UK_SGrid_Bristol",
    "T2_UK_SGrid_RALPP", "T2_US_Caltech", "T2_US_Florida", "T2_US_MIT", "T2_US_Nebraska", "T2_US_Purdue", "T2_US_UCSD", "T2_US_Vanderbilt", "T2_US_Wisconsin"
]
backend.siteinfo.ready_sites = lambda: set(backend.siteinfo.site_list())

from dynamo_consistency import picker


class TestPickRegex(unittest.TestCase):
    def setUp(self):
        os.remove(os.path.join(os.path.dirname(__file__), 'www', 'stats.db'))

    def loop(self, pattern):
        try:
            while True:
                self.assertFalse(picker.pick_site(pattern) == 'T1_UK_RAL_Disk')
        except picker.NoMatchingSite:
            pass

    def test_no_ral(self):
        # Set all T2s to running
        self.loop('^T2_')

        # Set all other T1s
        self.loop('(?<!_RAL)_Disk')

        # Only RAL is left
        self.assertEqual(picker.pick_site(), 'T1_UK_RAL_Disk')
        self.assertRaises(picker.NoMatchingSite, picker.pick_site)



if __name__ == '__main__':
    unittest.main(argv=base.ARGS)
