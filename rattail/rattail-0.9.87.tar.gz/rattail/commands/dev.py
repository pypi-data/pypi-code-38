# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Development Commands
"""

from __future__ import unicode_literals, absolute_import

import os
import re
import sys

from mako.template import Template

from rattail import commands
from rattail.files import resource_path


def main(*args):
    """
    Entry point for ``rattail-dev`` command.
    """
    Command().run(*args or sys.argv[1:])


class Command(commands.Command):
    """
    Rattail - development commands
    """
    name = 'rattail-dev'
    description = __doc__.strip()


class NewBatch(commands.Subcommand):
    """
    Generate some code for a new batch type.
    """
    name = 'new-batch'
    description = __doc__.strip()

    def add_parser_args(self, parser):
        parser.add_argument('--output-dir', '-O', default='.',
                            help="Path to which generated files should be written; "
                            "defaults to current directory.")
        parser.add_argument('model',
                            help="Name of primary model for new batch, e.g. "
                            "'VendorCatalog' or 'PrintLabels'.")

    def run(self, args):
        model_title = re.sub(r'([a-z])([A-Z])', r'\g<1> \g<2>', args.model)
        table_name = model_title.lower().replace(' ', '_')
        context = {
            'model_name': args.model,
            'model_title': model_title,
            'table_name': table_name,
        }
        template_dir = resource_path('rattail:data/new-batch')
        for name in ('model', 'handler', 'webview'):
            template_path = os.path.join(template_dir, '{}.py'.format(name))
            template = Template(filename=template_path)
            output_path = os.path.join(args.output_dir, '{}.py'.format(name))
            with open(output_path, 'wt') as output_file:
                output_file.write(template.render(**context))
