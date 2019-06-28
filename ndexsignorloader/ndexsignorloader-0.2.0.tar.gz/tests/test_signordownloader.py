#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `SignorDownloader` class."""

import os
import tempfile
import shutil
from mock import MagicMock

import unittest
from ndex2.nice_cx_network import NiceCXNetwork
from ndexsignorloader.ndexloadsignor import SignorDownloader


class TestSignorDownloader(unittest.TestCase):
    """Tests for `NodeMemberUpdator` class."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def get_fake_signor_pf_text(self):
        return """"SIGNOR ID";"PROT. FAMILY NAME";"LIST OF ENTITIES"
SIGNOR-PF1;ERK1/2;"P27361,  P28482"
SIGNOR-PF2;LPAR;"Q9HBW0,  Q9UBY5,  Q92633"
SIGNOR-PF3;Ggamma;"P63211,  P61952,  O14610,  P50151,  P63218,  Q9UBI6,  Q9UK08,  P59768,  P50150,  Q9P2W3,  O60262,  P63215"
SIGNOR-PF4;Gbeta;"P27361,  P28482"
"""

    def write_fake_signor_pf_file(self, destfile):
        with open(destfile, 'w') as f:
            f.write(self.get_fake_signor_pf_text())

    def get_fake_signor_complexes_text(self):
        return """"SIGNOR ID";"COMPLEX NAME";"LIST OF ENTITIES"
SIGNOR-C1;NFY;"P23511,  P25208,  Q13952"
SIGNOR-C2;mTORC2;"P68104,  Q8TB45"
"""

    def write_fake_signor_complexes_file(self, destfile):
        with open(destfile, 'w') as f:
            f.write(self.get_fake_signor_complexes_text())

    def test_get_pathway_list_file(self):
        dloader = SignorDownloader(None, 'f')
        self.assertEqual(os.path.join('f',
                                      SignorDownloader.PATHWAY_LIST_FILE),
                                      dloader.get_pathway_list_file())

    def test_get_complexes_file(self):
        dloader = SignorDownloader(None, 'f')
        self.assertEqual(os.path.join('f',
                                      SignorDownloader.COMPLEXES_FILE),
                                      dloader.get_complexes_file())

    def test_get_proteinfamily_map(self):
        temp_dir = tempfile.mkdtemp()
        try:
            dloader = SignorDownloader(None, temp_dir)
            pfile = dloader.get_proteinfamily_file()
            self.write_fake_signor_pf_file(pfile)
            res = dloader.get_proteinfamily_map()
            self.assertEqual(['P27361', 'P28482'], res['ERK1/2'])
            self.assertEqual(['P27361', 'P28482'], res['SIGNOR-PF1'])
            self.assertEqual(['Q9HBW0', 'Q9UBY5', 'Q92633'], res['LPAR'])
            self.assertEqual(['Q9HBW0', 'Q9UBY5', 'Q92633'], res['SIGNOR-PF2'])
        finally:
            shutil.rmtree(temp_dir)

    def test_get_complexes_map(self):
        temp_dir = tempfile.mkdtemp()
        try:
            dloader = SignorDownloader(None, temp_dir)
            pfile = dloader.get_complexes_file()
            self.write_fake_signor_complexes_file(pfile)
            res = dloader.get_complexes_map()
            self.assertEqual(['P23511', 'P25208', 'Q13952'], res['NFY'])
            self.assertEqual(['P23511', 'P25208', 'Q13952'], res['SIGNOR-C1'])

            self.assertEqual(['P68104', 'Q8TB45'], res['mTORC2'])
            self.assertEqual(['P68104', 'Q8TB45'], res['SIGNOR-C2'])

        finally:
            shutil.rmtree(temp_dir)

    def test_get_pathways_map(self):
        temp_dir = tempfile.mkdtemp()
        try:
            dloader = SignorDownloader(None, temp_dir)
            with open(dloader.get_pathway_list_file(), 'w') as f:
                f.write('SIGNOR-AC\tAdipogenesis\n')
                f.write('SIGNOR-AD\tAlzheimer Disease\n')
                f.write('SIGNOR-AML\tAcute Myeloid Leukemia\n')
                f.write('SIGNOR-AML-IDH/TET\tAML-IDH/TET\n')

            res = dloader.get_pathways_map()
            self.assertEqual('Adipogenesis', res['SIGNOR-AC'])
            self.assertEqual('Alzheimer Disease', res['SIGNOR-AD'])
            self.assertEqual('Acute Myeloid Leukemia', res['SIGNOR-AML'])
            self.assertEqual('AML-IDH/TET', res['SIGNOR-AML-IDHTET'])
        finally:
            shutil.rmtree(temp_dir)

    def test_get_download_url(self):
        dloader = SignorDownloader('hi', None)
        self.assertEqual('hi/' +
                         SignorDownloader.PATHWAYDATA_DOWNLOAD_SCRIPT +
                         'haha', dloader._get_download_url('haha'))

        self.assertEqual('hi/' +
                         SignorDownloader.PATHWAYDATA_DOWNLOAD_SCRIPT +
                         'haha&relations=only',
                         dloader._get_download_url('haha',
                                                   relationsonly=True))

    def test_get_fulldownload_url(self):
        dloader = SignorDownloader('hi', None)
        self.assertEqual('hi/' + SignorDownloader.GETDATA_SCRIPT +
                         'yo',
                         dloader._get_fulldownload_url('yo'))

