# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 GNS3 Technologies Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
import time
import logging
import asyncio
import socket

class uBridgeProtocol(asyncio.Protocol):

    def __init__(self, loop):

        self.transport = None
        self.on_con_lost = loop.create_future()

    def connection_made(self, transport):

        print("Connection made")
        self.transport = transport
        #self.transport.write("hypervisor version\n".encode())

    def data_received(self, data):
        print("Received:", data.decode())
        self.transport.close()

    def connection_lost(self, exc):
        print('The server closed the connection')
        # The socket has been closed
        self.on_con_lost.set_result(True)

# async def main():
#     # Get a reference to the event loop as we plan to use
#     # low-level APIs.
#     loop = asyncio.get_running_loop()
#
#     # Create a pair of connected sockets
#     rsock, wsock = socket.socketpair()
#
#     # Register the socket to wait for data.
#     transport, protocol = await loop.create_connection(
#         lambda: MyProtocol(loop), sock=rsock)
#
#     # Simulate the reception of data from the network.
#     loop.call_soon(wsock.send, 'abc'.encode())
#
#     try:
#         await protocol.on_con_lost
#     finally:
#         transport.close()
#         wsock.close()
#
# asyncio.run(main())

loop = asyncio.get_event_loop()

async def main():
    # Get a reference to the event loop as we plan to use
    # low-level APIs.
    #loop = asyncio.get_running_loop()

    transport, protocol = await loop.create_connection(lambda: uBridgeProtocol(loop), '127.0.0.1', 8888)
    transport.write("hypervisor version\n".encode())

    # Wait until the protocol signals that the connection
    # is lost and close the transport.
    try:
        await protocol.on_con_lost
    finally:
        transport.close()

loop.run_until_complete(main())
# Run the event loop
#loop.run_forever()
