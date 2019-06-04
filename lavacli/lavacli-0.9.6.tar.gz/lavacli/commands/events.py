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
import sys
from urllib.parse import urlparse
import zmq
from zmq.utils.strtypes import b, u


def configure_parser(parser, version):
    sub = parser.add_subparsers(dest="sub_sub_command", help="Sub commands")
    sub.required = True

    # "listen"
    listen_parser = sub.add_parser("listen", help="listen to events")
    listen_parser.add_argument(
        "--filter",
        action="append",
        default=None,
        choices=["device", "event", "testjob", "worker"],
        help="filter by topic type",
    )

    # "wait"
    if version >= (2018, 1):
        wait_parser = sub.add_parser("wait", help="wait for a specific event")
        obj_parser = wait_parser.add_subparsers(dest="object", help="object to wait")
        obj_parser.required = True

        # "wait device"
        device_parser = obj_parser.add_parser("device")
        device_parser.add_argument("hostname", type=str, help="hostname of the device")
        device_parser.add_argument(
            "--state",
            default=None,
            choices=["IDLE", "RESERVED", "RUNNING"],
            help="device state",
        )
        device_parser.add_argument(
            "--health",
            default=None,
            choices=["GOOD", "UNKNOWN", "LOOPING", "BAD", "MAINTENANCE", "RETIRED"],
            help="device health",
        )

        # "wait job"
        testjob_parser = obj_parser.add_parser("job")
        testjob_parser.add_argument("job_id", help="job id")
        testjob_parser.add_argument(
            "--state",
            default=None,
            choices=[
                "SUBMITTED",
                "SCHEDULING",
                "SCHEDULED",
                "RUNNING",
                "CANCELING",
                "FINISHED",
            ],
            help="job state",
        )
        testjob_parser.add_argument(
            "--health",
            default=None,
            choices=["UNKNOWN", "COMPLETE", "INCOMPLETE", "CANCELED"],
            help="job health",
        )

        # "wait worker"
        worker_parser = obj_parser.add_parser("worker")
        worker_parser.add_argument("hostname", type=str, help="worker hostname")
        worker_parser.add_argument(
            "--state", default=None, choices=["ONLINE", "OFFLINE"], help="worker state"
        )
        worker_parser.add_argument(
            "--health",
            default=None,
            choices=["ACTIVE", "MAINTENANCE", "RETIRED"],
            help="worker health",
        )


def help_string():
    return "listen to events"


def _get_zmq_url(proxy, options, config):
    if config is None or config.get("events", {}).get("uri") is None:
        url = proxy.scheduler.get_publisher_event_socket()
        if "*" in url:
            domain = urlparse(options.uri).netloc
            if "@" in domain:
                domain = domain.split("@")[1]
            domain = domain.split(":")[0]
            url = url.replace("*", domain)
    else:
        url = config["events"]["uri"]

    return url


def handle_listen(proxy, options, config):
    # Try to find the socket url
    url = _get_zmq_url(proxy, options, config)
    if url is None:
        print("Unable to find the socket url")
        return 1

    context = zmq.Context()
    sock = context.socket(zmq.SUB)
    sock.setsockopt(zmq.SUBSCRIBE, b"")
    # Set the sock proxy (if needed)
    socks = config.get("events", {}).get("socks_proxy")
    if socks is not None:
        print("Listening to %s (socks %s)" % (url, socks))
        sock.setsockopt(zmq.SOCKS_PROXY, b(socks))
    else:
        print("Listening to %s" % url)

    try:
        sock.connect(url)
    except zmq.error.ZMQError as exc:
        print("Unable to connect: %s" % exc)
        return 1

    while True:
        msg = sock.recv_multipart()
        try:
            (topic, _, dt, username, data) = (u(m) for m in msg)
        except ValueError:
            print("Invalid message: %s" % msg)
            continue

        # If unknown, print the full data
        msg = data
        data = json.loads(data)
        # Print according to the topic
        topic_end = topic.split(".")[-1]

        # filter by topic_end
        if options.filter and topic_end not in options.filter:
            continue

        if topic_end == "device":
            if config["version"] >= (2018, 1):
                msg = "[%s] <%s> state=%s health=%s" % (
                    data["device"],
                    data["device_type"],
                    data["state"],
                    data["health"],
                )
            else:
                msg = "[%s] <%s> %s" % (
                    data["device"],
                    data["device_type"],
                    data["status"],
                )
            if "job" in data:
                msg += " for %s" % data["job"]
        elif topic_end == "testjob":
            if config["version"] >= (2018, 1):
                msg = "[%s] <%s> state=%s health=%s (%s)" % (
                    data["job"],
                    data.get("device", "??"),
                    data["state"],
                    data["health"],
                    data["description"],
                )
            else:
                msg = "[%s] <%s> %s (%s)" % (
                    data["job"],
                    data.get("device", "??"),
                    data["status"],
                    data["description"],
                )
        elif topic_end == "worker":
            msg = "[%s] state=%s health=%s" % (
                data["hostname"],
                data["state"],
                data["health"],
            )
        elif topic_end == "event":
            msg = "[%s] message=%s" % (data["job"], data["message"])

        if sys.stdout.isatty():
            print(
                "\033[1;30m%s\033[0m \033[1;37m%s\033[0m \033[32m%s\033[0m - %s"
                % (dt, topic, username, msg)
            )
        else:
            print("%s %s %s - %s" % (dt, topic, username, msg))


def handle_wait(proxy, options, config):
    # Try to find the socket url
    url = _get_zmq_url(proxy, options, config)
    if url is None:
        print("Unable to find the socket url")
        return 1

    context = zmq.Context()
    sock = context.socket(zmq.SUB)
    # Filter by topic (if needed)
    sock.setsockopt(zmq.SUBSCRIBE, b(config.get("events", {}).get("topic", "")))

    # Set the sock proxy (if needed)
    socks = config.get("events", {}).get("socks_proxy")
    if socks is not None:
        print("Listening to %s (socks %s)" % (url, socks))
        sock.setsockopt(zmq.SOCKS_PROXY, b(socks))
    else:
        print("Listening to %s" % url)

    try:
        sock.connect(url)
    except zmq.error.ZMQError as exc:
        print("Unable to connect: %s" % exc)
        return 1

    # "job" is called "testjob" in the events
    object_topic = options.object
    if object_topic == "job":
        object_topic = "testjob"

    # Wait for events
    while True:
        msg = sock.recv_multipart()
        try:
            (topic, _uuid, _dt, _username, data) = (u(m) for m in msg)
        except ValueError:
            print("Invalid message: %s" % msg)
            continue
        data = json.loads(data)

        # Filter by object
        obj = topic.split(".")[-1]
        if obj != object_topic:
            continue

        if object_topic == "device":
            if data.get("device") != options.hostname:
                continue
        elif object_topic == "testjob":
            if data.get("job") != options.job_id:
                continue
        else:
            if data.get("hostname") != options.hostname:
                continue

        # Filter by state
        if options.state is not None:
            if data.get("state") != options.state.capitalize():
                continue
        # Filter by health
        if options.health is not None:
            if data.get("health") != options.health.capitalize():
                continue

        return 0


def handle(proxy, options, config):
    handlers = {"listen": handle_listen, "wait": handle_wait}
    return handlers[options.sub_sub_command](proxy, options, config)
