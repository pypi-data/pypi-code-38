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
import json
import time
import yaml

from lavacli.utils import loader


def configure_parser(parser, version):
    sub = parser.add_subparsers(dest="sub_sub_command", help="Sub commands")
    sub.required = True

    # "add"
    devices_add = sub.add_parser("add", help="add a device")
    devices_add.add_argument("hostname", help="hostname of the device")
    devices_add.add_argument("--type", required=True, help="device-type")
    devices_add.add_argument("--worker", required=True, help="worker hostname")
    devices_add.add_argument("--description", default=None, help="device description")

    owner = devices_add.add_mutually_exclusive_group()
    owner.add_argument("--user", default=None, help="device owner")
    owner.add_argument("--group", default=None, help="device group owner")

    if version >= (2018, 1):
        devices_add.add_argument(
            "--health",
            default=None,
            choices=["GOOD", "UNKNOWN", "LOOPING", "BAD", "MAINTENANCE", "RETIRED"],
            help="device health",
        )
    else:
        devices_add.add_argument(
            "--status",
            default=None,
            choices=["OFFLINE", "IDLE", "RUNNING", "OFFLINING", "RETIRED", "RESERVED"],
            help="device status",
        )
        devices_add.add_argument(
            "--health",
            default=None,
            choices=["UNKNOWN", "PASS", "FAIL", "LOOPING"],
            help="device health status",
        )

    devices_add.add_argument(
        "--private",
        action="store_true",
        default=False,
        help="private device [default=public]",
    )

    # "dict"
    devices_dict = sub.add_parser("dict", help="device dictionary")
    dict_sub = devices_dict.add_subparsers(
        dest="sub_sub_sub_command", help="Sub commands"
    )
    dict_sub.required = True
    dict_get = dict_sub.add_parser("get", help="get the device dictionary")
    dict_get.add_argument("hostname", help="hostname of the device")
    dict_get.add_argument(
        "field", nargs="?", default=None, help="only show the given sub-fields"
    )
    dict_get.add_argument(
        "--context", default=None, help="job context for template rendering"
    )
    dict_get.add_argument(
        "--render",
        action="store_true",
        default=False,
        help="render the dictionary into a configuration",
    )

    dict_set = dict_sub.add_parser("set", help="set the device dictionary")
    dict_set.add_argument("hostname", help="hostname of the device")
    dict_set.add_argument(
        "config", type=argparse.FileType("r"), help="device dictionary file"
    )

    # "list"
    devices_list = sub.add_parser("list", help="list available devices")
    devices_list.add_argument(
        "--all",
        "-a",
        action="store_true",
        default=False,
        help="list every devices, inluding retired",
    )
    out_format = devices_list.add_mutually_exclusive_group()
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

    # "maintenance"
    if version >= (2018, 1):
        devices_maintenance = sub.add_parser(
            "maintenance", help="maintenance the device"
        )
        devices_maintenance.add_argument("hostname", help="device hostname")
        devices_maintenance.add_argument(
            "--force",
            default=False,
            action="store_true",
            help="force device maintenance by canceling running job",
        )
        devices_maintenance.add_argument(
            "--no-wait",
            dest="wait",
            default=True,
            action="store_false",
            help="do not wait for the device to be idle",
        )

    # "show"
    devices_show = sub.add_parser("show", help="show device details")
    devices_show.add_argument("hostname", help="device hostname")
    out_format = devices_show.add_mutually_exclusive_group()
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

    # "tags"
    devices_tags = sub.add_parser("tags", help="manage tags for the given device")
    tags_sub = devices_tags.add_subparsers(
        dest="sub_sub_sub_command", help="Sub commands"
    )
    tags_sub.required = True
    tags_add = tags_sub.add_parser("add", help="add a tag")
    tags_add.add_argument("hostname", help="hostname of the device")
    tags_add.add_argument("tag", help="name of the tag")

    tags_del = tags_sub.add_parser("delete", help="remove a tag")
    tags_del.add_argument("hostname", help="hostname of the device")
    tags_del.add_argument("tag", help="name of the tag")

    tags_list = tags_sub.add_parser("list", help="list tags for the device")
    tags_list.add_argument("hostname", help="hostname of the device")
    out_format = tags_list.add_mutually_exclusive_group()
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
        help="print as yaml",
    )

    # "update"
    devices_update = sub.add_parser("update", help="update device properties")
    devices_update.add_argument("hostname", help="hostname of the device")
    devices_update.add_argument("--worker", default=None, help="worker hostname")
    devices_update.add_argument(
        "--description", default=None, help="device description"
    )

    owner = devices_update.add_mutually_exclusive_group()
    owner.add_argument("--user", default=None, help="device owner")
    owner.add_argument("--group", default=None, help="device group owner")

    if version >= (2018, 1):
        devices_update.add_argument(
            "--health",
            default=None,
            choices=["GOOD", "UNKNOWN", "LOOPING", "BAD", "MAINTENANCE", "RETIRED"],
            help="device health",
        )
    else:
        devices_update.add_argument(
            "--status",
            default=None,
            choices=["OFFLINE", "IDLE", "RUNNING", "OFFLINING", "RETIRED", "RESERVED"],
            help="device status",
        )
        devices_update.add_argument(
            "--health",
            default=None,
            choices=["UNKNOWN", "PASS", "FAIL", "LOOPING"],
            help="device health status",
        )

    display = devices_update.add_mutually_exclusive_group()
    display.add_argument(
        "--public", default=None, action="store_true", help="make the device public"
    )
    display.add_argument(
        "--private", dest="public", action="store_false", help="make the device private"
    )


def help_string():
    return "manage devices"


def handle_add(proxy, options, config):
    if config["version"] >= (2018, 1):
        proxy.scheduler.devices.add(
            options.hostname,
            options.type,
            options.worker,
            options.user,
            options.group,
            not options.private,
            options.health,
            options.description,
        )
    else:
        proxy.scheduler.devices.add(
            options.hostname,
            options.type,
            options.worker,
            options.user,
            options.group,
            not options.private,
            options.status,
            options.health,
            options.description,
        )
    return 0


def _lookups(value, fields):
    try:
        for key in fields:
            if isinstance(value, list):
                value = value[int(key)]
            else:
                value = value[key]
    except IndexError:
        print("list index out of range (%d vs %d)" % (int(key), len(value)))
        return 1
    except KeyError:
        print("Unknow key '%s' for '%s'" % (key, value))
        return 1
    except TypeError:
        print("Unable to lookup inside '%s' for '%s'" % (value, key))
        return 1
    print(value)
    return 0


def handle_dict(proxy, options, _):
    if options.sub_sub_sub_command == "get":
        config = proxy.scheduler.devices.get_dictionary(
            options.hostname, options.render, options.context
        )
        if not options.field:
            print(str(config).rstrip("\n"))
            return 0

        if options.render:
            value = yaml.load(str(config), Loader=loader())
            return _lookups(value, options.field.split("."))
        else:
            # Extract some variables
            import jinja2

            env = jinja2.Environment(autoescape=False)  # nosec
            ast = env.parse(config)
            field_name = options.field.split(".")[0]

            # Loop on all assignments
            for assign in ast.find_all(jinja2.nodes.Assign):
                if assign.target.name == field_name:
                    value = assign.node.as_const()
                    if options.field == field_name:
                        print(value)
                        return 0
                    else:
                        return _lookups(value, options.field.split(".")[1:])
            print("Unknow field '%s'" % field_name)
            return 1

    else:
        config = options.config.read()
        ret = proxy.scheduler.devices.set_dictionary(options.hostname, config)
        if not ret:
            print("Unable to set the configuration")
        return 0 if ret else 1


def handle_list(proxy, options, config):
    devices = proxy.scheduler.devices.list(options.all)

    if options.output_format == "json":
        print(json.dumps(devices))
    elif options.output_format == "yaml":
        print(yaml.dump(devices).rstrip("\n"))
    else:
        print("Devices:")
        for device in devices:
            if config["version"] >= (2018, 1):
                print(
                    "* %s (%s): %s,%s"
                    % (
                        device["hostname"],
                        device["type"],
                        device["state"],
                        device["health"],
                    )
                )
            else:
                print(
                    "* %s (%s): %s"
                    % (device["hostname"], device["type"], device["status"])
                )
    return 0


def handle_maintenance(proxy, options, _):
    proxy.scheduler.devices.update(
        options.hostname, None, None, None, None, "MAINTENANCE", None
    )
    device = proxy.scheduler.devices.show(options.hostname)
    current_job = device["current_job"]
    if current_job is not None:
        print("-> waiting for job %s" % current_job)
        # if --force is passed, cancel the job
        if options.force:
            print("--> canceling")
            proxy.scheduler.jobs.cancel(current_job)
        while (
            options.wait
            and proxy.scheduler.jobs.show(current_job)["state"] != "Finished"
        ):
            print("--> waiting")
            time.sleep(5)
    return 0


def handle_show(proxy, options, config):
    device = proxy.scheduler.devices.show(options.hostname)

    if options.output_format == "json":
        print(json.dumps(device))
    elif options.output_format == "yaml":
        print(yaml.dump(device).rstrip("\n"))
    else:
        print("name        : %s" % device["hostname"])
        print("device-type : %s" % device["device_type"])
        if config["version"] >= (2018, 1):
            print("state       : %s" % device["state"])
            print("health      : %s" % device["health"])
        else:
            print("status      : %s" % device["status"])
        print("user        : %s" % device["user"])
        print("group       : %s" % device["group"])
        print("health job  : %s" % device["health_job"])
        print("description : %s" % device["description"])
        print("public      : %s" % device["public"])
        print("pipeline    : %s" % device["pipeline"])
        print("device-dict : %s" % device["has_device_dict"])
        print("worker      : %s" % device["worker"])
        print("current job : %s" % device["current_job"])
        print("tags        : %s" % device["tags"])
    return 0


def handle_tags(proxy, options, _):
    if options.sub_sub_sub_command == "add":
        proxy.scheduler.devices.tags.add(options.hostname, options.tag)
    elif options.sub_sub_sub_command == "delete":
        proxy.scheduler.devices.tags.delete(options.hostname, options.tag)
    else:
        tags = proxy.scheduler.devices.tags.list(options.hostname)
        if options.output_format == "json":
            print(json.dumps(tags))
        elif options.output_format == "yaml":
            print(yaml.dump(tags).rstrip("\n"))
        else:
            print("Tags:")
            for tag in tags:
                print("* %s" % tag)
    return 0


def handle_update(proxy, options, config):
    if config["version"] >= (2018, 1):
        proxy.scheduler.devices.update(
            options.hostname,
            options.worker,
            options.user,
            options.group,
            options.public,
            options.health,
            options.description,
        )
    else:
        proxy.scheduler.devices.update(
            options.hostname,
            options.worker,
            options.user,
            options.group,
            options.public,
            options.status,
            options.health,
            options.description,
        )
    return 0


def handle(proxy, options, config):
    handlers = {
        "add": handle_add,
        "dict": handle_dict,
        "list": handle_list,
        "maintenance": handle_maintenance,
        "show": handle_show,
        "tags": handle_tags,
        "update": handle_update,
    }
    return handlers[options.sub_sub_command](proxy, options, config)
