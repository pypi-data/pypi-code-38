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

import json
import yaml


def configure_parser(parser, version):
    sub = parser.add_subparsers(dest="sub_sub_command", help="Sub commands")
    sub.required = True

    # "add"
    aliases_add = sub.add_parser("add", help="add an alias")
    aliases_add.add_argument("alias", help="alias name")
    if version >= (2019, 5):
        aliases_add.add_argument("device_type", help="device-type")

    # "delete"
    aliases_del = sub.add_parser("delete", help="delete an alias")
    aliases_del.add_argument("alias", help="alias name")

    # "list"
    aliases_list = sub.add_parser("list", help="list available aliases")
    out_format = aliases_list.add_mutually_exclusive_group()
    out_format.add_argument(
        "--json",
        dest="output_format",
        default=None,
        action="store_const",
        const="json",
        help="print as json",
    )
    out_format.add_argument(
        "--yaml",
        dest="output_format",
        default=None,
        action="store_const",
        const="yaml",
        help="print as yaml",
    )

    # "show"
    aliases_show = sub.add_parser("show", help="show alias details")
    aliases_show.add_argument("alias", help="alias")
    out_format = aliases_show.add_mutually_exclusive_group()
    out_format.add_argument(
        "--json",
        dest="output_format",
        default=None,
        action="store_const",
        const="json",
        help="print as json",
    )
    out_format.add_argument(
        "--yaml",
        dest="output_format",
        action="store_const",
        const="yaml",
        default=None,
        help="print as yaml",
    )


def help_string():
    return "manage device-type aliases"


def handle_add(proxy, options, config):
    if config["version"] >= (2019, 5):
        proxy.scheduler.aliases.add(options.alias, options.device_type)
    else:
        proxy.scheduler.aliases.add(options.alias)
    return 0


def handle_delete(proxy, options, _):
    proxy.scheduler.aliases.delete(options.alias)
    return 0


def handle_list(proxy, options, _):
    aliases = proxy.scheduler.aliases.list()
    if options.output_format == "json":
        print(json.dumps(aliases))
    elif options.output_format == "yaml":
        print(yaml.dump(aliases).rstrip("\n"))
    else:
        print("Aliases:")
        for alias in aliases:
            print("* %s" % alias)
    return 0


def handle_show(proxy, options, config):
    alias = proxy.scheduler.aliases.show(options.alias)
    if options.output_format == "json":
        print(json.dumps(alias))
    elif options.output_format == "yaml":
        print(yaml.dump(alias).rstrip("\n"))
    else:
        if config["version"] >= (2019, 5):
            print("name       : %s" % alias["name"])
            print("device-type: %s" % alias["device_type"])
        else:
            print("name        : %s" % alias["name"])
            print("device-types:")
            for dt in alias["device_types"]:
                print("* %s" % dt)
    return 0


def handle(proxy, options, config):
    handlers = {
        "add": handle_add,
        "delete": handle_delete,
        "list": handle_list,
        "show": handle_show,
    }
    return handlers[options.sub_sub_command](proxy, options, config)
