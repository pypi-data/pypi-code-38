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

import contextlib
import pathlib
import shutil
import time
import xmlrpc.client
import yaml


def configure_parser(parser, version):
    sub = parser.add_subparsers(dest="sub_sub_command", help="Sub commands")
    sub.required = True

    # "active"
    if version >= (2017, 12):
        sub.add_parser("active", help="activate the system")

    #  "api"
    sub.add_parser("api", help="print server API version")

    # "export"
    sys_export = sub.add_parser("export", help="export server configuration")
    sys_export.add_argument("name", help="name of the export")
    sys_export.add_argument(
        "--full",
        default=False,
        action="store_true",
        help="do a full export, including retired devices",
    )

    # "import"
    # sub.add_parser("import", help="import server configuration")

    # "maintenance"
    if version >= (2017, 12):
        sys_maintenance = sub.add_parser("maintenance", help="maintenance the system")
        sys_maintenance.add_argument(
            "--force",
            default=False,
            action="store_true",
            help="force maintenance by canceling jobs",
        )
        sys_maintenance.add_argument(
            "--exclude",
            default=None,
            help="comma seperated list of workers to keep untouched",
        )

    # "methods"
    sys_methods = sub.add_parser("methods", help="list methods")
    sys_sub = sys_methods.add_subparsers(
        dest="sub_sub_sub_command", help="Sub commands"
    )
    sys_sub.required = True
    sys_sub.add_parser("list", help="list available methods")

    sys_help = sys_sub.add_parser("help", help="method help")
    sys_help.add_argument("method", help="method name")

    sys_signature = sys_sub.add_parser("signature", help="method signature")
    sys_signature.add_argument("method", help="method name")

    # "version"
    sub.add_parser("version", help="print the server version")

    # "whoami"
    sub.add_parser("whoami", help="print the current username")


def help_string():
    return "system information"


def handle_active(proxy, _, __):
    print("Activate workers:")
    workers = proxy.scheduler.workers.list()
    for worker in workers:
        print("* %s" % worker)
        proxy.scheduler.workers.update(worker, None, "ACTIVE")
    return 0


def handle_api(proxy, _, __):
    print(proxy.system.api_version())
    return 0


def handle_export(proxy, options, config):
    print("Export to %s" % options.name)
    dest = pathlib.Path(options.name)
    with contextlib.suppress(FileNotFoundError):
        shutil.rmtree(str(dest))
    with contextlib.suppress(FileExistsError):
        dest.mkdir(mode=0o755)

    print("Listing aliases")
    aliases = []
    for alias in proxy.scheduler.aliases.list():
        print("* %s" % alias)
        aliases.append(proxy.scheduler.aliases.show(alias))

    print("Listing tags")
    tags = []
    for tag in proxy.scheduler.tags.list():
        print("* %s" % tag["name"])
        tags.append(tag)

    print("Listing workers")
    workers = []
    for worker in proxy.scheduler.workers.list():
        print("* %s" % worker)
        w = proxy.scheduler.workers.show(worker)
        if config["version"] >= (2017, 12):
            workers.append(
                {
                    "hostname": w["hostname"],
                    "description": w["description"],
                    "state": w["state"],
                    "health": w["health"],
                }
            )
        else:
            workers.append(
                {
                    "hostname": w["hostname"],
                    "description": w["description"],
                    "master": w["master"],
                    "hidden": w["hidden"],
                }
            )

    print("Listing device-types")
    (dest / "device-types").mkdir(mode=0o755)
    device_types = []
    for device_type in proxy.scheduler.device_types.list():
        print("* %s" % device_type["name"])
        dt = proxy.scheduler.device_types.show(device_type["name"])
        device_types.append(
            {
                "name": dt["name"],
                "description": dt["description"],
                "display": dt["display"],
                "health_disabled": dt["health_disabled"],
                "owners_only": dt["owners_only"],
                "aliases": dt["aliases"],
            }
        )

        try:
            dt_template = proxy.scheduler.device_types.get_template(dt["name"])
        except xmlrpc.client.Fault as exc:
            if exc.faultCode == 404:
                print("  => No template found")
                continue
            raise
        with (dest / "device-types" / ("%s.jinja2" % dt["name"])).open(
            "w", encoding="utf-8"
        ) as f_out:
            f_out.write(str(dt_template))

    print("Listing devices")
    (dest / "devices").mkdir(mode=0o755)
    devices = []
    for device in proxy.scheduler.devices.list(options.full):
        print("* %s" % device["hostname"])
        d = proxy.scheduler.devices.show(device["hostname"])
        devices.append(
            {
                "hostname": d["hostname"],
                "description": d["description"],
                "device_type": d["device_type"],
                "pipeline": d["pipeline"],
                "worker": d["worker"],
                "state": d["state"],
                "health": d["health"],
                "public": d["public"],
                "user": d["user"],
                "group": d["group"],
                "tags": d["tags"],
            }
        )

        try:
            device_dict = proxy.scheduler.devices.get_dictionary(device["hostname"])
        except xmlrpc.client.Fault as exc:
            if exc.faultCode == 404:
                print("  => No device dict found")
                continue
            raise
        with (dest / "devices" / ("%s.jinja2" % device["hostname"])).open(
            "w", encoding="utf-8"
        ) as f_out:
            f_out.write(str(device_dict))

    export = {
        "aliases": aliases,
        "devices": devices,
        "device-types": device_types,
        "tags": tags,
        "workers": workers,
    }

    # Dump the configuration
    with (dest / "instance.yaml").open("w", encoding="utf-8") as f_out:
        f_out.write(yaml.dump(export).rstrip("\n"))
    return 0


def handle_maintenance(proxy, options, _):
    print("Maintenance workers:")
    workers = proxy.scheduler.workers.list()
    excluded_workers = []
    if options.exclude:
        excluded_workers = options.exclude.split(",")
    for worker in workers:
        if worker in excluded_workers:
            print("* %s [SKIP]" % worker)
            continue
        print("* %s" % worker)
        proxy.scheduler.workers.update(worker, None, "MAINTENANCE")

    excluded_devices = []
    if excluded_workers:
        for worker in excluded_workers:
            excluded_devices.extend(proxy.scheduler.workers.show(worker)["devices"])

    print("Wait for devices:")
    devices = proxy.scheduler.devices.list()
    for device in devices:
        if device["hostname"] in excluded_devices:
            continue
        print("* %s" % device["hostname"])
        current_job = device["current_job"]
        if current_job is not None:
            print("--> waiting for job %s" % current_job)
            # if --force is passed, cancel the job
            if options.force:
                print("---> canceling")
                proxy.scheduler.jobs.cancel(current_job)
            while proxy.scheduler.jobs.show(current_job)["state"] != "Finished":
                print("---> waiting")
                time.sleep(5)
    return 0


def handle_methods(proxy, options, _):
    if options.sub_sub_sub_command == "help":
        print(proxy.system.methodHelp(options.method))
    elif options.sub_sub_sub_command == "signature":
        print(proxy.system.methodSignature(options.method))
    else:
        # Fallback to "list"
        methods = proxy.system.listMethods()
        for method in methods:
            print(method)
    return 0


def handle_version(proxy, _, __):
    print(proxy.system.version())
    return 0


def handle_whoami(proxy, _, __):
    username = proxy.system.whoami()
    if username is None:
        print("<AnonymousUser>")
    else:
        print(username)
    return 0


def handle(proxy, options, config):
    handlers = {
        "active": handle_active,
        "api": handle_api,
        "export": handle_export,
        "maintenance": handle_maintenance,
        "methods": handle_methods,
        "version": handle_version,
        "whoami": handle_whoami,
    }
    return handlers[options.sub_sub_command](proxy, options, config)
