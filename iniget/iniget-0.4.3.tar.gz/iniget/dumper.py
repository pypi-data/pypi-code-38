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

import six, json
from .loader import configparser, Config, Section, isstr

list_types = (list, tuple, set)

#------------------------------------------------------------------------------
class Dumper(object):

  #----------------------------------------------------------------------------
  def __init__(self, jsonify=False):
    self.jsonify = jsonify

  #----------------------------------------------------------------------------
  def dumpfp(self, data, fp, jsonify_lists=False):
    if self.jsonify:
      fp.write(json.dumps(data))
      fp.write('\n')
      return
    if isinstance(data, Config):
      for section, options in data.items():
        # todo: ensure this escape mechanism is ok with ConfigParser...
        section = section.replace('\\', '\\\\').replace(']', '\\]')
        fp.write('[{}]\n'.format(section))
        self.dumpfp(options, fp)
      return
    if isinstance(data, Section):
      for option, value in data.items():
        fp.write(option)
        fp.write(' = ')
        self.dumpfp(data[option], fp, jsonify_lists=True)
      return
    if not jsonify_lists and isinstance(data, list_types):
      for item in data:
        fp.write(item)
        fp.write('\n')
      return
    if isstr(data):
      fp.write(data)
    else:
      fp.write(json.dumps(data))
    fp.write('\n')

default = Dumper()

#------------------------------------------------------------------------------
def dump(data, fp, dumper=None, *args, **kw):
  if dumper is None:
    if args or kw:
      dumper = Dumper(*args, **kw)
    else:
      dumper = default
  if isstr(fp):
    with open(fp, 'rb') as fp:
      return dump(data, fp, dumper=dumper)
  return dumper.dumpfp(data, fp)

#------------------------------------------------------------------------------
def dumps(data, *args, **kw):
  out = six.StringIO()
  dump(data, out, *args, **kw)
  return out.getvalue()

#------------------------------------------------------------------------------
# end of $Id$
# $ChangeLog$
#------------------------------------------------------------------------------
