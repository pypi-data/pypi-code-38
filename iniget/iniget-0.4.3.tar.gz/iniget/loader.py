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

import collections
import json

import six
import iniherit
from six.moves import configparser

#------------------------------------------------------------------------------

DEFAULT_SECTION = configparser.DEFAULTSECT

#------------------------------------------------------------------------------
def isstr(obj):
  return isinstance(obj, six.string_types)

#------------------------------------------------------------------------------
class Config(collections.OrderedDict): pass
class Section(collections.OrderedDict): pass

#------------------------------------------------------------------------------
def sectkey(sect):
  if sect == DEFAULT_SECTION:
    return -100
  return sect

truthy = frozenset(('true', 'yes', 'on'))
falsy  = frozenset(('false', 'no', 'off'))

#------------------------------------------------------------------------------
class Loader(object):

  #----------------------------------------------------------------------------
  def __init__(self, inherit=True, case_sensitive=True,
               defaults=None, interpolate=True, fallback=True,
               jsonify=True):
    self.inherit      = inherit
    self.case         = case_sensitive
    self.defaults     = defaults
    self.interpolate  = interpolate
    self.jsonify      = jsonify
    self.fallback     = fallback

  #----------------------------------------------------------------------------
  def loadfp(self, fp):
    data = fp.read()
    attr = 'SafeConfigParser' if self.interpolate else 'RawConfigParser'
    mod  = iniherit if self.inherit else configparser
    ini  = getattr(mod, attr)(defaults=self.defaults)
    inir = getattr(mod, 'RawConfigParser')(defaults=self.defaults)
    ini.optionxform = str if self.case else str.lower
    inir.optionxform = str if self.case else str.lower
    ini.readfp(six.StringIO(data))
    inir.readfp(six.StringIO(data))
    def getopt(sect, opt):
      try:
        return ini.get(sect, opt)
      except Exception:
        if not self.interpolate or not self.fallback:
          raise
        return inir.get(sect, opt)
    ret = Config()
    ret[DEFAULT_SECTION] = Section()
    for opt in ini.defaults().keys():
      ret[DEFAULT_SECTION][opt] = getopt(DEFAULT_SECTION, opt)
    for section in sorted(ini.sections(), key=sectkey):
      ret[section] = Section()
      for opt in ini.options(section):
        ret[section][opt] = getopt(section, opt)
    if self.jsonify is False:
      return ret
    jret = Config()
    for sectname, options in ret.items():
      section = Section()
      for option, value in options.items():
        section[option] = self.parse(value)
      jret[sectname] = section
    return jret

  #----------------------------------------------------------------------------
  def parse(self, value):
    if value in truthy:
      return True
    if value in falsy:
      return False
    try:
      # todo: make this sensitive to self.jsonify being a range of values...
      #       eg. at jsonify==0.1, only parse scalars. at jsonify=0.2, also
      #       parse lists. at jsonify>=1.0 and is True, go all out.
      return json.loads(value)
    except ValueError:
      return value

default = Loader()

#------------------------------------------------------------------------------
def loadfp(fp, loader=None, *args, **kws):
  if loader is None:
    if args or kws:
      loader = Loader(*args, **kws)
    else:
      loader = default
  return loader.loadfp(fp)

#------------------------------------------------------------------------------
def loads(data, *args, **kws):
  return loadfp(six.StringIO(data), *args, **kws)

#------------------------------------------------------------------------------
def load(filename, *args, **kws):
  if not isstr(filename):
    return loadfp(filename, *args, **kws)
  # todo: *** hack alert *** this **SHOULD** just call `Loader` with a
  #       `filename` parameter... but this is the easiest way to make
  #       the `test.py:test_dirchange_relative_iniherit` scenario work...
  # todo: escape `filename`...
  data = '[DEFAULT]\n%inherit = ' + filename
  return loads(data, *args, **kws)

#------------------------------------------------------------------------------
# end of $Id$
# $ChangeLog$
#------------------------------------------------------------------------------
