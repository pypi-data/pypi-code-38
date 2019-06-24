# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@metagriffin.net>
# date: 2013/09/04
# copy: (C) Copyright 2013-EOT metagriffin -- see LICENSE.txt
#------------------------------------------------------------------------------
# This software is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.
#------------------------------------------------------------------------------

import unittest
import os
import textwrap

import six
import fso

from . import loader, sifter, dumper

#------------------------------------------------------------------------------
class TestIniget(unittest.TestCase):

  #----------------------------------------------------------------------------
  def test_load(self):
    ini = '[DEFAULT]\na = b\n[sect1]\nc = true\n'
    chk = {'DEFAULT': {'a': 'b'}, 'sect1': {'a': 'b', 'c': True}}
    out = loader.load(six.StringIO(ini))
    self.assertEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_loads(self):
    ini = '[DEFAULT]\na = b\n[sect1]\nc = true\nC = e\n'
    chk = {'DEFAULT': {'a': 'b'}, 'sect1': {'a': 'b', 'c': True, 'C': 'e'}}
    out = loader.loads(ini)
    self.assertEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_loads_icase(self):
    ini = '[DEFAULT]\na = b\n[sect1]\nc = true\nC = e\n'
    chk = {'DEFAULT': {'a': 'b'}, 'sect1': {'a': 'b', 'c': 'e'}}
    out = loader.loads(ini, case_sensitive=False)
    self.assertEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_loads_moreTruthy(self):
    ini = '[DEFAULT]\na = b\nb = true\nc = on\nd = yes\n'
    chk = {'DEFAULT': {'a': 'b', 'b': True, 'c': True, 'd': True}}
    out = loader.loads(ini)
    self.assertEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_loads_moreFalsy(self):
    ini = '[DEFAULT]\na = b\nb = false\nc = off\nd = no\n'
    chk = {'DEFAULT': {'a': 'b', 'b': False, 'c': False, 'd': False}}
    out = loader.loads(ini)
    self.assertEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_loads_defaultsMissing(self):
    ini = '[DEFAULT]\na = b\n[sect1]\nc = no-such-%(here)s-data\n'
    with self.assertRaises(loader.configparser.InterpolationMissingOptionError) as cm:
      out = loader.loads(ini, fallback=False)
    self.assertEqual(cm.exception.reference, 'here')

  #----------------------------------------------------------------------------
  def test_loads_defaults(self):
    ini = '[DEFAULT]\na = b\n[sect1]\nc = no-such-%(here)s-data\n'
    chk = {'DEFAULT': {'a': 'b', 'here': 'str'},
           'sect1': {'a': 'b', 'c': 'no-such-str-data', 'here': 'str'}}
    out = loader.loads(ini, defaults=dict(here='str'))
    self.assertEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_evaluates_default_section(self):
    ini = '[DEFAULT]\na = b\nc = %(a)s\n'
    chk = {'DEFAULT': {'a': 'b', 'c': 'b'}}
    out = loader.loads(ini)
    self.assertEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_bad_interpolation_value(self):
    ini = '[logger]\ndatefmt = %Y-%m-%d\n'
    chk = {'DEFAULT': {}, 'logger': {'datefmt': '%Y-%m-%d'}}
    out = loader.loads(ini)
    self.assertEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_loads_nointerpolate(self):
    ini = '[DEFAULT]\na = b\n[sect1]\nc = no-such-%(here)s-data\n'
    chk = {'DEFAULT': {'a': 'b'}, 'sect1': {'a': 'b', 'c': 'no-such-%(here)s-data'}}
    out = loader.loads(ini, interpolate=False)
    self.assertEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_load_jsonify(self):
    ini = '[DEFAULT]\na = b\n[sect1]\nc = true\ne = true\nf = 12\n'
    chk = {'DEFAULT': {'a': 'b'}, 'sect1': {'a': 'b', 'c': True, 'e': True, 'f': 12}}
    out = loader.load(six.StringIO(ini))
    self.assertEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_load_nojsonify(self):
    ini = '[DEFAULT]\na = b\n[sect1]\nc = true\ne = true\nf = 12\n'
    chk = {'DEFAULT': {'a': 'b'}, 'sect1': {'a': 'b', 'c': 'true', 'e': 'true', 'f': '12'}}
    out = loader.load(six.StringIO(ini), jsonify=False)
    self.assertEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_sift_sections(self):
    ini = loader.loads('[DEFAULT]\na = b\n[sect1]\nc = true\n')
    chk = ['DEFAULT', 'sect1']
    out = sifter.sift(ini, list_sections=True)
    self.assertEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_sift_keysAllSections(self):
    ini = loader.loads('[DEFAULT]\na = b\n[sect1]\nc = true\n')
    chk = {'DEFAULT': ['a'], 'sect1': ['a', 'c']}
    out = sifter.sift(ini, list_keys=True)
    self.assertEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_sift_keysOneSectionStr(self):
    ini = loader.loads('[DEFAULT]\na = b\n[sect1]\nc = true\n[sect2]\ne = f\n')
    chk = ['a', 'c']
    out = sifter.sift(ini, list_keys=True, sections='sect1')
    self.assertEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_sift_keysOneSectionList(self):
    ini = loader.loads('[DEFAULT]\na = b\n[sect1]\nc = true\n[sect2]\ne = f\n')
    chk = {'sect1': ['a', 'c']}
    out = sifter.sift(ini, list_keys=True, sections=['sect1'])
    self.assertEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_sift_keysMultipleSections(self):
    ini = loader.loads('[DEFAULT]\na = b\n[sect1]\nc = true\n[sect2]\ne = f\n')
    chk = {'sect1': ['a', 'c'], 'sect2': ['a', 'e']}
    out = sifter.sift(ini, list_keys=True, sections=['sect1', 'sect2'])
    self.assertEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_sift_getSectKeyStr(self):
    ini = loader.loads('[DEFAULT]\na = b\n[sect1]\nc = true\n[sect2]\ne = f\n')
    chk = 'f'
    out = sifter.sift(ini, sections='sect2', keys='e')
    self.assertEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_sift_noSectKey(self):
    ini = loader.loads('[DEFAULT]\na = b\n[sect1]\nc = true\n[sect2]\ne = f\n')
    with self.assertRaises(loader.configparser.NoSectionError) as cm:
      out = sifter.sift(ini, sections='no-such-sect', keys='e')
    self.assertIn('no-such-sect', cm.exception.message)

  #----------------------------------------------------------------------------
  def test_sift_sectNoKey(self):
    ini = loader.loads('[DEFAULT]\na = b\n[sect1]\nc = true\n[sect2]\ne = f\n')
    with self.assertRaises(loader.configparser.NoOptionError) as cm:
      out = sifter.sift(ini, sections='sect1', keys='no-such-key')
    self.assertIn('no-such-key', cm.exception.message)

  #----------------------------------------------------------------------------
  def test_sift_getSectKeyListOne(self):
    ini = loader.loads('[DEFAULT]\na = b\n[sect1]\nc = true\n[sect2]\ne = f\n')
    chk = {'c': True}
    out = sifter.sift(ini, sections='sect1', keys=['c'])
    self.assertEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_sift_getSectKeyListMultiple(self):
    ini = loader.loads('[DEFAULT]\na = b\n[sect1]\nc = true\n[sect2]\ne = f\n')
    chk = {'a': 'b', 'c': True}
    out = sifter.sift(ini, sections='sect1', keys=['a', 'c'])
    self.assertEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_sift_getSectsKey(self):
    ini = loader.loads('[DEFAULT]\na = b\n[sect1]\nc = true\n[sect2]\ne = f\n')
    chk = {'sect1': {'a': 'b'}, 'sect2': {'a': 'b'}}
    out = sifter.sift(ini, sections=['sect1', 'sect2'], keys=['a'])
    self.assertEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_sift_getSectsKeys(self):
    ini = loader.loads('[DEFAULT]\na = b\n[sect1]\nc = true\n[sect2]\nc = false\ne = f\n')
    chk = {'sect1': {'a': 'b', 'c': True}, 'sect2': {'a': 'b', 'c': False}}
    out = sifter.sift(ini, sections=['sect1', 'sect2'], keys=['a', 'c'])
    self.assertEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_sift_getSectsKeysNoSect(self):
    ini = loader.loads('[DEFAULT]\na = b\n[sect1]\nc = true\n[sect2]\nc = true2\ne = f\n')
    chk = {'sect1': {'a': 'b', 'c': 'd'}, 'sect2': {'a': 'b', 'c': 'd2'}}
    with self.assertRaises(loader.configparser.NoSectionError) as cm:
      out = sifter.sift(ini, sections=['sect1', 'sect2', 'no-such-sect'], keys=['a', 'c'])
    self.assertIn('no-such-sect', cm.exception.message)

  #----------------------------------------------------------------------------
  def test_sift_getSectsKeysNoKey(self):
    ini = loader.loads('[DEFAULT]\na = b\n[sect1]\nc = true\n[sect2]\ne = f\n')
    chk = {'sect1': {'a': 'b', 'c': 'd'}, 'sect2': {'a': 'b', 'c': 'd2'}}
    with self.assertRaises(loader.configparser.NoOptionError) as cm:
      out = sifter.sift(ini, sections=['sect1', 'sect2'], keys=['a', 'no-such-key'])
    self.assertIn('no-such-key', cm.exception.message)
    self.assertIn('sect1', cm.exception.message)

  #----------------------------------------------------------------------------
  def test_dump(self):
    ini = loader.loads('[DEFAULT]\na = b\n[sect1]\nc = true\n[sect2]\nc = true2\ne = f\n')
    ini = sifter.sift(ini, sections='sect1', keys='c')
    out = six.StringIO()
    dumper.dump(ini, out)
    chk = 'true\n'
    self.assertMultiLineEqual(out.getvalue(), chk)

  #----------------------------------------------------------------------------
  def test_dumps(self):
    ini = loader.loads('[DEFAULT]\na = b\n[sect1]\nc = true\n[sect2]\nc = true2\ne = f\n')
    ini = sifter.sift(ini, sections='sect1', keys='c')
    out = dumper.dumps(ini)
    chk = 'true\n'
    self.assertMultiLineEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_dumps_listSects(self):
    ini = loader.loads('[DEFAULT]\na = b\n[sect1]\nc = true\n[sect2]\nc = true2\ne = f\n')
    ini = sifter.sift(ini, list_sections=True)
    out = dumper.dumps(ini)
    chk = 'DEFAULT\nsect1\nsect2\n'
    self.assertMultiLineEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_dumps_listSectsJson(self):
    ini = loader.loads('[DEFAULT]\na = b\n[sect1]\nc = true\n[sect2]\nc = true2\ne = f\n')
    ini = sifter.sift(ini, list_sections=True)
    out = dumper.dumps(ini, jsonify=True)
    chk = '["DEFAULT", "sect1", "sect2"]\n'
    self.assertMultiLineEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_dumps_listKeys(self):
    ini = loader.loads('[DEFAULT]\na = b\n[sect1]\nc = true\n[sect2]\nc = true2\ne = f\n')
    ini = sifter.sift(ini, list_keys=True)
    out = dumper.dumps(ini)
    chk = '[DEFAULT]\na\n[sect1]\na\nc\n[sect2]\na\nc\ne\n'
    self.assertMultiLineEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_dumps_listKeysJson(self):
    ini = loader.loads('[DEFAULT]\na = b\n[sect1]\nc = true\n[sect2]\nc = true2\ne = f\n')
    ini = sifter.sift(ini, list_keys=True)
    out = dumper.dumps(ini, jsonify=True)
    chk = '{"DEFAULT": ["a"], "sect1": ["a", "c"], "sect2": ["a", "c", "e"]}\n'
    self.assertMultiLineEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_dumps_listKeysJson_ordering(self):
    ini = loader.loads('[DEFAULT]\na = b\n[sect2]\ne = f\nc = true2\n[sect1]\nc = true\n')
    ini = sifter.sift(ini, list_keys=True)
    out = dumper.dumps(ini, jsonify=True)
    chk = '{"DEFAULT": ["a"], "sect1": ["a", "c"], "sect2": ["a", "c", "e"]}\n'
    self.assertMultiLineEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_dumps_section(self):
    ini = loader.loads('[DEFAULT]\na = b\n[sect1]\nd = foo\nc = true\n')
    ini = sifter.sift(ini, sections='sect1')
    out = dumper.dumps(ini)
    chk = 'd = foo\nc = true\na = b\n'
    self.assertMultiLineEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_dumps_sectionJson(self):
    ini = loader.loads('[DEFAULT]\na = b\n[sect1]\nc = true\nd = foo\n')
    ini = sifter.sift(ini, sections='sect1')
    out = dumper.dumps(ini, jsonify=True)
    chk = '{"c": true, "d": "foo", "a": "b"}\n'
    self.assertMultiLineEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_dumps_value(self):
    ini = loader.loads('[DEFAULT]\na = b\n[sect2]\ne = f\nc = true2\n[sect1]\nc = true\n')
    ini = sifter.sift(ini, sections='sect2', keys='c')
    out = dumper.dumps(ini)
    chk = 'true2\n'
    self.assertMultiLineEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_dumps_valueJson(self):
    ini = loader.loads('[DEFAULT]\na = b\n[sect2]\ne = f\nc = true2\n[sect1]\nc = true\n')
    ini = sifter.sift(ini, sections='sect2', keys='c')
    out = dumper.dumps(ini, jsonify=True)
    chk = '"true2"\n'
    self.assertMultiLineEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_nodirchange_relative_iniherit(self):
    with fso.push() as overlay:
      with open('base.ini', 'wb') as fp:
        fp.write(textwrap.dedent('''\
          [DEFAULT]
          alpha = beta
        '''))
      with open('config.ini', 'wb') as fp:
        fp.write(textwrap.dedent('''\
          [DEFAULT]
          %inherit = base.ini
        '''))
      result = loader.load('config.ini')
      self.assertEqual(result.get('DEFAULT').get('alpha'), 'beta')

  #----------------------------------------------------------------------------
  def test_dirchange_relative_iniherit(self):
    with fso.push() as overlay:
      os.makedirs('.nosuchdir/configs')
      with open('.nosuchdir/configs/base.ini', 'wb') as fp:
        fp.write(textwrap.dedent('''\
          [DEFAULT]
          alpha = beta
        '''))
      with open('.nosuchdir/configs/config.ini', 'wb') as fp:
        fp.write(textwrap.dedent('''\
          [DEFAULT]
          %inherit = base.ini
        '''))
      result = loader.load('.nosuchdir/configs/config.ini')
      self.assertEqual(result.get('DEFAULT').get('alpha'), 'beta')


#------------------------------------------------------------------------------
# end of $Id$
# $ChangeLog$
#------------------------------------------------------------------------------
