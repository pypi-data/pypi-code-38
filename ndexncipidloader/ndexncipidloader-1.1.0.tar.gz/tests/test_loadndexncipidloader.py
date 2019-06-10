#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ndexncipidloader` package."""

import os
import tempfile
import shutil

import unittest
from ndexutil.config import NDExUtilConfig
from ndexncipidloader import loadndexncipidloader
from ndexncipidloader.loadndexncipidloader import NetworkAttributes
from ndexncipidloader.loadndexncipidloader import NetworkAttributesFromTSVFactory


class TestNdexncipidloader(unittest.TestCase):
    """Tests for `ndexncipidloader` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_parse_arguments(self):
        """Tests parse arguments"""
        res = loadndexncipidloader._parse_arguments('hi',
                                                    ['foo'])

        self.assertEqual(res.profile, 'ndexncipidloader')
        self.assertEqual(res.verbose, 0)
        self.assertEqual(res.logconf, None)
        self.assertEqual(res.conf, None)

        someargs = ['-vv', '--conf', 'foo', '--logconf', 'hi',
                    '--loadplan', 'plan',
                    '--networkattrib', 'net',
                    '--style', 'style',
                    '--profile', 'myprofy', 'doublefoo']
        res = loadndexncipidloader._parse_arguments('hi', someargs)

        self.assertEqual(res.profile, 'myprofy')
        self.assertEqual(res.verbose, 2)
        self.assertEqual(res.logconf, 'hi')
        self.assertEqual(res.conf, 'foo')

    def test_setup_logging(self):
        """ Tests logging setup"""
        try:
            loadndexncipidloader._setup_logging(None)
            self.fail('Expected AttributeError')
        except AttributeError:
            pass

        # args.logconf is None
        res = loadndexncipidloader._parse_arguments('hi', ['--loadplan',
                                                           'plan',
                                                           '--networkattrib',
                                                           'net',
                                                           '--style',
                                                           'style',
                                                           'foo'])
        loadndexncipidloader._setup_logging(res)

        # args.logconf set to a file
        try:
            temp_dir = tempfile.mkdtemp()

            logfile = os.path.join(temp_dir, 'log.conf')
            with open(logfile, 'w') as f:
                f.write("""[loggers]
keys=root

[handlers]
keys=stream_handler

[formatters]
keys=formatter

[logger_root]
level=DEBUG
handlers=stream_handler

[handler_stream_handler]
class=StreamHandler
level=DEBUG
formatter=formatter
args=(sys.stderr,)

[formatter_formatter]
format=%(asctime)s %(name)-12s %(levelname)-8s %(message)s""")

            res = loadndexncipidloader._parse_arguments('hi', ['--logconf',
                                                               logfile,
                                                               '--loadplan',
                                                               'plan',
                                                               '--networkattrib',
                                                               'net',
                                                               '--style',
                                                               'style',
                                                               temp_dir])
            loadndexncipidloader._setup_logging(res)

        finally:
            shutil.rmtree(temp_dir)

    def test_main(self):
        """Tests main function"""

        # try where loading config is successful
        try:
            temp_dir = tempfile.mkdtemp()
            confile = os.path.join(temp_dir, 'some.conf')
            with open(confile, 'w') as f:
                f.write("""[hi]
                {user} = bob
                {pw} = smith
                {server} = dev.ndexbio.org""".format(user=NDExUtilConfig.USER,
                                                     pw=NDExUtilConfig.PASSWORD,
                                                     server=NDExUtilConfig.SERVER))
            res = loadndexncipidloader.main(['myprog.py', '--conf',
                                             confile, '--profile', 'hi',
                                             '--loadplan', 'plan',
                                             '--networkattrib', 'net',
                                             '--style', 'style',
                                             temp_dir])
            self.assertEqual(res, 2)
        finally:
            shutil.rmtree(temp_dir)

    def test_networkattributes(self):
        na = NetworkAttributes()
        self.assertEqual(na.get_author(None), None)
        self.assertEqual(na.get_labels(None), None)
        self.assertEqual(na.get_reviewers(None), None)

        na.add_author_entry('boo', 'bauthor')
        self.assertEqual(na.get_author(None), None)
        self.assertEqual(na.get_labels(None), None)
        self.assertEqual(na.get_reviewers(None), None)
        self.assertEqual(na.get_author('boo'), 'bauthor')
        self.assertEqual(na.get_labels('boo'), None)
        self.assertEqual(na.get_reviewers('boo'), None)
        self.assertEqual(na.get_author('far'), None)
        self.assertEqual(na.get_labels('far'), None)
        self.assertEqual(na.get_reviewers('far'), None)

        na.add_labels_entry('boo', 'clabel')
        self.assertEqual(na.get_author(None), None)
        self.assertEqual(na.get_labels(None), None)
        self.assertEqual(na.get_reviewers(None), None)
        self.assertEqual(na.get_author('boo'), 'bauthor')
        self.assertEqual(na.get_labels('boo'), 'clabel')
        self.assertEqual(na.get_reviewers('boo'), None)
        self.assertEqual(na.get_author('far'), None)
        self.assertEqual(na.get_labels('far'), None)
        self.assertEqual(na.get_reviewers('far'), None)

        na.add_reviewers_entry('boo', 'dreviewer')
        self.assertEqual(na.get_author(None), None)
        self.assertEqual(na.get_labels(None), None)
        self.assertEqual(na.get_reviewers(None), None)
        self.assertEqual(na.get_author('boo'), 'bauthor')
        self.assertEqual(na.get_labels('boo'), 'clabel')
        self.assertEqual(na.get_reviewers('boo'), 'dreviewer')
        self.assertEqual(na.get_author('far'), None)
        self.assertEqual(na.get_labels('far'), None)
        self.assertEqual(na.get_reviewers('far'), None)

        na.add_labels_entry('well', 'there')
        self.assertEqual(na.get_labels('well'), 'there')

        na.add_reviewers_entry('yoyo', 'hh')
        self.assertEqual(na.get_reviewers('yoyo'), 'hh')

    def test_networkattributesfromtsvfactory(self):
        try:
            fac = NetworkAttributesFromTSVFactory(None, delim=',')
            self.assertEqual(fac.get_network_attributes_obj(), None)

            temp_dir = tempfile.mkdtemp()
            tsvfile = loadndexncipidloader.get_networkattributes()
            fac = NetworkAttributesFromTSVFactory(tsvfile, delim='\t')
            na = fac.get_network_attributes_obj()
            self.assertEqual(na.get_labels('a4b7 Integrin signaling'),
                             'a4b7_pathway')
            self.assertEqual(na.get_reviewers('a4b7 Integrin signaling'),
                             'David Rose, Francisco Sanchez-Madrid, Maria Mittelbrunn')
            self.assertEqual(na.get_author('a4b7 Integrin signaling'),
                             'Shiva Krupa')
        finally:
            shutil.rmtree(temp_dir)
