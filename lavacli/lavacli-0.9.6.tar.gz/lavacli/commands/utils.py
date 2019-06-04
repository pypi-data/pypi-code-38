# -*- coding: utf-8 -*-
# vim: set ts=4

# Copyright 2017 Rémi Duraffort
# This file is part of lavacli.
#
# lavacli is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# lavacli is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with lavacli.  If not, see <http://www.gnu.org/licenses/>

import argparse
import jinja2
import yaml

from lavacli.utils import loader
from . import jobs


def configure_parser(parser, _):
    sub = parser.add_subparsers(dest="sub_sub_command", help="Sub commands")
    sub.required = True

    # "logs"
    logs = sub.add_parser("logs", help="log helpers")
    logs_sub = logs.add_subparsers(dest="sub_sub_sub_command", help="Sub commands")
    logs_sub.required = True

    # "logs.print"
    logs_print = logs_sub.add_parser("print", help="print log file")
    logs_print.add_argument("filename", type=argparse.FileType("r"), help="log file")
    logs_print.add_argument(
        "--filters",
        default=None,
        type=str,
        help="comma seperated list of levels to show",
    )
    logs_print.add_argument(
        "--raw", default=False, action="store_true", help="print raw logs"
    )

    # "templates"
    templates = sub.add_parser("templates", help="template helpers")
    templates_sub = templates.add_subparsers(
        dest="sub_sub_sub_command", help="Sub commands"
    )
    templates_sub.required = True

    # "templates.render"
    # TODO: add an option to be strict about undefined variables
    templates_render = templates_sub.add_parser("render", help="render jinja2 template")
    templates_render.add_argument(
        "filename", type=argparse.FileType("r"), help="template"
    )
    templates_render.add_argument(
        "--path", type=str, action="append", help="templates lookup path"
    )
    templates_render.add_argument(
        "--context", type=str, action="append", default=[], help="context variables"
    )
    templates_render.add_argument(
        "--trim", action="store_true", default=False, help="trim blocks"
    )


def help_string():
    return "utility functions"


def handle_logs(_, options):
    try:
        logs = yaml.load(options.filename.read(), Loader=loader(False))
    except yaml.YAMLError:
        print("Invalid yaml file")
    else:
        jobs.print_logs(logs, options.raw, options.filters)


def handle_templates(_, options):
    assert options.sub_sub_sub_command == "render"
    # Set the default value here
    # If we give it to argparse, then it's always present even when --path is
    # passed.
    if options.path is None:
        options.path = ["/etc/lava-server/dispatcher-config/device-types"]

    env = jinja2.Environment(
        autoescape=False,
        trim_blocks=options.trim,
        loader=jinja2.FileSystemLoader(options.path),
    )
    data = options.filename.read()
    template = env.from_string(data)

    # Build the context
    try:
        context = {k.split("=")[0]: k.split("=")[1] for k in options.context}
    except Exception:
        print("Invalid context variable")
        print("Should be of the form key=value")
        return 1
    try:
        print(template.render(**context))
        return 0
    except jinja2.TemplateNotFound:
        print("Unable to find the templates")
        return 1


def handle(proxy, options, _):
    handlers = {"logs": handle_logs, "templates": handle_templates}
    return handlers[options.sub_sub_command](proxy, options)
