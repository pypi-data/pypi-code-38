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
import os
import requests
import socket
from urllib.parse import urlparse
import xmlrpc.client
import yaml

from .__about__ import __version__
from .utils import loader, parse_version, VERSION_LATEST, exc2str

from .commands import (
    aliases,
    devices,
    device_types,
    events,
    identities,
    jobs,
    results,
    system,
    tags,
    utils,
    workers,
)


class RequestsTransport(xmlrpc.client.Transport):
    def __init__(self, scheme, proxy=None, timeout=20.0, verify_ssl_cert=True):
        super().__init__()
        self.scheme = scheme
        # Set the user agent
        self.user_agent = "lavacli v%s" % __version__
        if proxy is None:
            self.proxies = {}
        else:
            self.proxies = {scheme: proxy}
        self.timeout = timeout
        self.verify_ssl_cert = verify_ssl_cert
        if not verify_ssl_cert:
            from requests.packages.urllib3.exceptions import InsecureRequestWarning

            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    def request(self, host, handler, request_body, verbose=False):
        headers = {
            "User-Agent": self.user_agent,
            "Content-Type": "text/xml",
            "Accept-Encoding": "gzip",
        }
        url = "%s://%s%s" % (self.scheme, host, handler)
        try:
            response = None
            response = requests.post(
                url,
                data=request_body,
                headers=headers,
                timeout=self.timeout,
                verify=self.verify_ssl_cert,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return self.parse_response(response)
        except requests.RequestException as e:
            if response is None:
                raise xmlrpc.client.ProtocolError(url, 500, str(e), "")
            else:
                raise xmlrpc.client.ProtocolError(
                    url, response.status_code, str(e), response.headers
                )

    def parse_response(self, response):
        """
        Parse the xmlrpc response.
        """
        p, u = self.getparser()
        p.feed(response.text)
        p.close()
        return u.close()


def load_config(identity):
    # Build the path to the configuration file
    config_dir = os.environ.get("XDG_CONFIG_HOME", "~/.config")
    config_filename = os.path.expanduser(os.path.join(config_dir, "lavacli.yaml"))

    try:
        with open(config_filename, "r", encoding="utf-8") as f_conf:
            config = yaml.load(f_conf.read(), Loader=loader())
        return config[identity]
    except (FileNotFoundError, KeyError, TypeError):
        return {}


def common_parser():
    parser_obj = argparse.ArgumentParser(add_help=False)

    # --help and --version
    misc = parser_obj.add_argument_group("lavacli")

    misc.add_argument(
        "--help",
        "-h",
        action="store_true",
        default=False,
        help="show this help message and exit",
    )
    misc.add_argument(
        "--version",
        action="store_true",
        default=False,
        help="print the version number and exit",
    )

    # identity or url
    url = parser_obj.add_argument_group("identity").add_mutually_exclusive_group()
    url.add_argument(
        "--uri", type=str, default=None, help="URI of the lava-server RPC endpoint"
    )
    url.add_argument(
        "--identity",
        "-i",
        metavar="ID",
        type=str,
        default="default",
        help="identity stored in the configuration",
    )

    return parser_obj


def parser(parser_obj, commands, version):
    # The sub commands
    root = parser_obj.add_subparsers(dest="sub_command", help="Sub commands")

    keys = list(commands.keys())
    keys.sort()
    for name in keys:
        cls = commands[name]
        cls.configure_parser(root.add_parser(name, help=cls.help_string()), version)

    return parser_obj


def main():
    # List of known commands
    commands = {
        "aliases": aliases,
        "devices": devices,
        "device-types": device_types,
        "events": events,
        "identities": identities,
        "jobs": jobs,
        "results": results,
        "system": system,
        "tags": tags,
        "utils": utils,
        "workers": workers,
    }

    # Parsing is made of two phases as arguments depends on the API version of
    # the remote server.
    # 1/ Parse the common arguments
    parser_obj = common_parser()
    (options, remaining) = parser_obj.parse_known_args()

    # Do we have to print the version numer?
    if options.version:
        print("lavacli %s" % __version__)
        return 0

    # Print help if lavacli is called without any arguments
    if not remaining:
        parser_obj = parser(parser_obj, commands, VERSION_LATEST)
        parser_obj.print_help()
        return 0 if options.help else 1

    # Load the configuration (if any)
    uri = options.uri
    proxy = None
    version = VERSION_LATEST
    config = {}

    # Skip when sub_command is "identities"
    if remaining[0] not in ["identities", "utils"]:
        if uri is None:
            config = load_config(options.identity)
            if config.get("uri") is None:
                print("Unknown identity '%s'" % options.identity)
                return 1
            username = config.get("username")
            token = config.get("token")
            if username is not None and token is not None:
                p = urlparse(config["uri"])
                uri = "%s://%s:%s@%s%s" % (p.scheme, username, token, p.netloc, p.path)
            else:
                uri = config["uri"]

        try:
            # Create the Transport object
            parsed_uri = urlparse(uri)
            transport = RequestsTransport(
                parsed_uri.scheme,
                config.get("proxy"),
                config.get("timeout", 20.0),
                config.get("verify_ssl_cert", True),
            )
            # allow_none is True because the server does support it
            proxy = xmlrpc.client.ServerProxy(uri, allow_none=True, transport=transport)
            version = proxy.system.version()
        except (OSError, xmlrpc.client.Error) as exc:
            print("Unable to connect: %s" % exc2str(exc))
            return 1

        # Parse version
        version = parse_version(version)
    config["version"] = version

    # Parse the command line
    parser_obj = parser(parser_obj, commands, version)
    options = parser_obj.parse_args()
    options.uri = uri

    try:
        # Run the command
        return commands[options.sub_command].handle(proxy, options, config)
    except (ConnectionError, socket.gaierror) as exc:
        print("Unable to connect to '%s': %s" % (options.uri, str(exc)))

    except KeyboardInterrupt:
        pass

    except identities.ConfigurationError as exc:
        print(exc)
        return 1
    except xmlrpc.client.Error as exc:
        msg = exc.errmsg if hasattr(exc, "errmsg") else str(exc)
        if "sub_sub_command" in options:
            print(
                "Unable to call '%s.%s': %s"
                % (options.sub_command, options.sub_sub_command, msg)
            )
        else:
            print("Unable to call '%s': %s" % (options.sub_command, msg))
    except BaseException as exc:
        print("Unknown error: %s" % str(exc))

    return 1
