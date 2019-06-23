#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# jp: a SAT command line tool
# Copyright (C) 2009-2019 Jérôme Poisson (goffi@goffi.org)
# Copyright (C) 2013-2016 Adrien Cossa (souliane@mailoo.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import base
from sat.core.i18n import _
__commands__ = ["Param"]


class Get(base.CommandBase):
    def __init__(self, host):
        super(Get, self).__init__(host, 'get', need_connect=False, help=_('Get a parameter value'))

    def add_parser_options(self):
        self.parser.add_argument("category", nargs='?', type=base.unicode_decoder, help=_(u"Category of the parameter"))
        self.parser.add_argument("name", nargs='?', type=base.unicode_decoder, help=_(u"Name of the parameter"))
        self.parser.add_argument("-a", "--attribute", type=str, default="value", help=_(u"Name of the attribute to get"))
        self.parser.add_argument("--security-limit", type=int, default=-1, help=_(u"Security limit"))

    def start(self):
        if self.args.category is None:
            categories = self.host.bridge.getParamsCategories()
            print u"\n".join(categories)
        elif self.args.name is None:
            try:
                values_dict = self.host.bridge.asyncGetParamsValuesFromCategory(self.args.category, self.args.security_limit, self.profile)
            except Exception as e:
                print u"Can't find requested parameters: {}".format(e)
                self.host.quit(1)
            for name, value in values_dict.iteritems():
                print u"{}\t{}".format(name, value)
        else:
            try:
                value = self.host.bridge.asyncGetParamA(self.args.name, self.args.category, self.args.attribute,
                                                                  self.args.security_limit, self.profile)
            except Exception as e:
                print u"Can't find requested parameter: {}".format(e)
                self.host.quit(1)
            print value


class Set(base.CommandBase):
    def __init__(self, host):
        super(Set, self).__init__(host, 'set', need_connect=False, help=_('Set a parameter value'))

    def add_parser_options(self):
        self.parser.add_argument("category", type=base.unicode_decoder, help=_(u"Category of the parameter"))
        self.parser.add_argument("name", type=base.unicode_decoder, help=_(u"Name of the parameter"))
        self.parser.add_argument("value", type=base.unicode_decoder, help=_(u"Name of the parameter"))
        self.parser.add_argument("--security-limit", type=int, default=-1, help=_(u"Security limit"))

    def start(self):
        try:
            self.host.bridge.setParam(self.args.name, self.args.value, self.args.category, self.args.security_limit, self.profile)
        except Exception as e:
            print u"Can set requested parameter: {}".format(e)


class SaveTemplate(base.CommandBase):
    def __init__(self, host):
        super(SaveTemplate, self).__init__(host, 'save', use_profile=False, help=_('Save parameters template to xml file'))

    def add_parser_options(self):
        self.parser.add_argument("filename", type=str, help=_("Output file"))

    def start(self):
        """Save parameters template to xml file"""
        if self.host.bridge.saveParamsTemplate(self.args.filename):
            print _("Parameters saved to file %s") % self.args.filename
        else:
            print _("Can't save parameters to file %s") % self.args.filename


class LoadTemplate(base.CommandBase):

    def __init__(self, host):
        super(LoadTemplate, self).__init__(host, 'load', use_profile=False, help=_('Load parameters template from xml file'))

    def add_parser_options(self):
        self.parser.add_argument("filename", type=str, help=_("Input file"))

    def start(self):
        """Load parameters template from xml file"""
        if self.host.bridge.loadParamsTemplate(self.args.filename):
            print _("Parameters loaded from file %s") % self.args.filename
        else:
            print _("Can't load parameters from file %s") % self.args.filename


class Param(base.CommandBase):
    subcommands = (Get, Set, SaveTemplate, LoadTemplate)

    def __init__(self, host):
        super(Param, self).__init__(host, 'param', use_profile=False, help=_('Save/load parameters template'))
