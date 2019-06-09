import logging
import os
from unittest import TestCase, mock

import settings
import estimate


# class QualityControlTest(TestCase):
#     def setUp(self):
#         self.dcb = DownloadDCB(YEAR, DAY)
#         logging.disable(logging.ERROR)
#
#     def test_file_name(self):
#         """Must return the name CAS0MGXRAP_2018160000_01D_01D_DCB.BSX.gz"""
#         self.assertEqual('CAS0MGXRAP_2018160000_01D_01D_DCB.BSX.gz', self.dcb.file)