#
#   Copyright 2018 University of Lancaster
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import argparse
import asyncio
import configparser
import logging

from typing import Any

import websockets  # type: ignore

from .endpoint import Endpoint
from .jwt_issuer import JWTIssuer

try:
    import aiomonitor  # type: ignore
except ImportError:
    aiomonitor = None


# Default websocket port
DEFAULT_WEBSOCKET_LISTEN_PORT = 8765


class Application:
    def __init__(self) -> None:
        self.parse_args_and_configure()

    def parse_args_and_configure(self) -> None:
        parser = argparse.ArgumentParser(
            description="Expose PostgresQL server connections over WebSockets")

        parser.add_argument('config', help="Path to configuration file")
        parser.add_argument(
            '--port', default=DEFAULT_WEBSOCKET_LISTEN_PORT, type=int,
            help="port to listen for websocket connections")
        parser.add_argument(
            '-v', '--verbose', action='store_true',
            help="include debug log entries")
        parser.add_argument(
            '-m', '--monitor', action='store_true',
            help="start aiomonitor instance")
        parser.add_argument(
            '-t', '--trust-x-forwarded-for', action='store_true',
            help="trust the X-Forwarded-For header (reverse-proxy setup)")

        self.args = parser.parse_args()

        if self.args.monitor and aiomonitor is None:
            parser.error("--monitor requires the aiomonitor package")

        self.config = configparser.ConfigParser(allow_no_value=True)
        with open(self.args.config) as config_file:
            self.config.read_file(config_file)

        asyncio.get_event_loop().set_debug(self.args.verbose)

        log_level = logging.DEBUG if self.args.verbose else logging.INFO
        logging.basicConfig(level=log_level)

        self.endpoints = {}  # type: Dict[str, Endpoint]
        self.jwt_issuers = {}  # type: Dict[str, JWTIssuer]

        for key in self.config.sections():
            if key.startswith("/"):
                self.endpoints[key] = Endpoint(self, key)
            else:
                self.jwt_issuers[key] = JWTIssuer(self, key)

    async def start(self) -> None:
        await asyncio.gather(*[endpoint.start() for endpoint in self.endpoints.values()])

        await websockets.serve(self.websocket_handler, port=self.args.port)
        msg = "Listening for websocket connections on *:{}"
        logging.info(msg.format(self.args.port))

        logging.info("Ready")

    async def websocket_handler(self, websocket: Any, path: str) -> None:
        endpoint = self.endpoints.get(path)

        if not endpoint:
            msg = "No endpoint registered at {!r}"
            msg = msg.format(path)

            logging.warning("Rejecting connection: {}".format(msg))
            await websocket.close(4001, msg)
            return

        await endpoint.websocket_handler(websocket)


def run() -> None:
    application = Application()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(application.start())

    monitor = None

    if application.args.monitor:
        monitor = aiomonitor.Monitor(loop)

        logging.info("Starting aiomonitor")
        monitor.start()

    try:
        loop.run_forever()
    finally:
        if monitor:
            monitor.close()
