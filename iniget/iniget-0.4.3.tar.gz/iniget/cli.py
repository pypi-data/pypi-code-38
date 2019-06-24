# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@metagriffin.net>
# date: 2013/08/20
# copy: (C) Copyright 2014-EOT metagriffin -- see LICENSE.txt
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

import sys, argparse, json
from . import loader, sifter, dumper
from .i18n import _

#------------------------------------------------------------------------------
def main(argv=None):

  cli = argparse.ArgumentParser(
    description = _(
      'Simple tool to extract, normalize, and JSONify values from an'
      ' iniherit-enabled "INI" configuration file.'),
    )

  cli.add_argument(
    _('-s'), _('--section'), metavar=_('SECTION'),
    dest='sections', action='append', default=[],
    help=_('specify additional sections to extract from; can be'
           ' specified multiple times to add multiple sections'))

  cli.add_argument(
    _('-C'), _('--no-case'),
    dest='case', action='store_false', default=True,
    help=_('handle option names case insensitively'))

  cli.add_argument(
    _('-I'), _('--no-inherit'),
    dest='inherit', action='store_false', default=True,
    help=_('disable processing of "%%inherit" directives'))

  cli.add_argument(
    _('-E'), _('--no-expansion'),
    dest='interpolate', action='store_false', default=True,
    help=_('disable ConfigParser option expansion ("interpolation")'))

  cli.add_argument(
    _('-F'), _('--no-fallback'),
    dest='fallback', action='store_false', default=True,
    help=_('disable falling back to non-interpolated option expansion'))

  cli.add_argument(
    _('-K'), _('--list-options'),
    dest='list_keys', action='store_true', default=False,
    help=_('list the option names only, not the values'))

  cli.add_argument(
    _('-S'), _('--list-sections'),
    dest='list_sections', action='store_true', default=False,
    help=_('list the section names only'))

  cli.add_argument(
    _('-J'), _('--json-parse'),
    dest='json_parse', action='store_true', default=False,
    help=_('if option values are JSON-parseable, parse as such;'
           ' additionally, the following are interpreted as boolean'
           ' values: {}', list(reversed(sorted(list(loader.truthy)
                                               + list(loader.falsy))))))

  cli.add_argument(
    _('-j'), _('--json-output'),
    dest='json_output', action='store_true', default=False,
    help=_('render the output using JSON syntax'))

  cli.add_argument(
    _('-d'), _('--defaults'), metavar=_('JSON'),
    dest='defaults', action='store',
    help=_('set the ConfigParser default values from this JSON-parsed'
           ' dictionary'))

  cli.add_argument(
    _('-r'), _('--raw'),
    dest='raw', action='store_true', default=False,
    help=_('don\'t do anything fancy: show exactly what ConfigParser'
           ' interprets (requires exactly one section and one option);'
           ' note that options "--no-case", "--no-inherit", "--no-expansion"'
           ' and "--defaults" are still honored, but "--json-parse" is not'))

  cli.add_argument(
    'config', metavar=_('FILENAME'),
    help=_('path to INI configuration file; if exactly "-", the'
           ' configuration is read from STDIN'))

  cli.add_argument(
    'section', metavar=_('SECTION'),
    nargs='?',
    help=_('configuration section to extract from; if not specified or'
           ' exactly "-", select all sections'))

  cli.add_argument(
    'keys', metavar=_('OPTION'),
    nargs='*',
    help=_('configuration option to extract; if not specified or'
           ' exactly "-", list all option/value pairs in the selected'
           ' section(s)'))

  options = cli.parse_args(args=argv)

  # todo: confirm that empty section/key names are indeed not valid...

  # clean up section names
  if options.section == '-':
    options.section = None
  options.sections.append(options.section)
  options.sections = filter(None, options.sections)
  if not options.sections:
    options.sections = None
  elif len(options.sections) == 1:
    options.sections = options.sections[0]

  # clean up key names
  if options.keys == ['-']:
    options.keys = None
  options.keys = filter(None, options.keys)
  if not options.keys:
    options.keys = None
  elif len(options.keys) == 1:
    options.keys = options.keys[0]

  if options.config == '-':
    options.config = sys.stdin

  if options.defaults:
    try:
      options.defaults = json.loads(options.defaults)
    except Exception as err:
      cli.error(_('"--defaults" must specify a JSON dictionary;'
                  ' parsing error: ', options.defaults) + str(err))

  if options.raw:
    if not loader.isstr(options.sections) or not loader.isstr(options.keys):
      cli.error(_('raw mode ("--raw") requires exactly one section and'
                  ' one option to be specified'))
    options.json_parse = False

  result = loader.load(
    options.config,
    inherit     = options.inherit, case_sensitive=options.case,
    interpolate = options.interpolate, defaults=options.defaults,
    fallback    = options.fallback,
    jsonify     = options.json_parse,
  )

  try:
    if options.raw:
      if options.sections not in result:
        raise loader.configparser.NoSectionError(section=options.sections)
      section = result[options.sections]
      if options.keys not in section:
        raise loader.configparser.NoOptionError(section=options.sections,
                                                option=options.keys)
      print repr(section[options.keys])
      return 0
    result = sifter.sift(
      result,
      list_keys=options.list_keys, list_sections=options.list_sections,
      sections=options.sections, keys=options.keys)
  except loader.configparser.NoSectionError as err:
    print >>sys.stderr, _('ERROR: no such section "{}"', err.section)
    return 20
  except loader.configparser.NoOptionError as err:
    print >>sys.stderr, _('ERROR: no such option "{}" in section "{}"',
                          err.option, err.section)
    return 21

  dumper.dump(
    result, sys.stdout,
    jsonify=options.json_output)
  return 0

#------------------------------------------------------------------------------
# end of $Id$
# $ChangeLog$
#------------------------------------------------------------------------------
