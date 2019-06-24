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

import six
from .loader import DEFAULT_SECTION, configparser, Config, Section, isstr, sectkey

#------------------------------------------------------------------------------
def sift(data,
         list_sections=False, list_keys=False,
         sections=None, keys=None):

  if list_sections:
    return sorted(data.keys(), key=sectkey)

  if list_keys:
    if isstr(sections):
      try:
        return sorted(data[sections].keys())
      except KeyError:
        raise configparser.NoSectionError(section=sections)
    try:
      ret = Config()
      for section in sorted(sections or data.keys(), key=sectkey):
        ret[section] = sorted(data[section].keys())
      return ret
    except KeyError as err:
      raise configparser.NoSectionError(section=err.message)

  if isstr(sections):
    if sections not in data:
      raise configparser.NoSectionError(section=sections)
    section = data[sections]
    if isstr(keys):
      try:
        return section[keys]
      except KeyError:
        raise configparser.NoOptionError(section=sections, option=keys)
    if keys is None:
      return section
    try:
      ret = Section()
      for key in sorted(keys):
        ret[key] = section[key]
      return ret
    except KeyError:
      raise configparser.NoOptionError(section=sections, option=keys)

  ret = Config()
  for sectname in sorted(sections or data.keys(), key=sectkey):
    if sectname not in data:
      raise configparser.NoSectionError(section=sectname)
    section = data[sectname]
    ret[sectname] = Section()
    for key in sorted(keys or section.keys()):
      if key not in section:
        raise configparser.NoOptionError(section=sectname, option=key)
      ret[sectname][key] = section[key]
  return ret

#------------------------------------------------------------------------------
# end of $Id$
# $ChangeLog$
#------------------------------------------------------------------------------
