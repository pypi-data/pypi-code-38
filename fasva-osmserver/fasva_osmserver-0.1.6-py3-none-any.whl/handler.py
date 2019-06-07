# -*- tab-width: 4; encoding: utf-8; -*-
# ex: set tabstop=4 expandtab:
# Copyright (c) 2016-2018 by Lars Klitzke, Lars.Klitzke@hs-emden-leer.de.
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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import asyncio
import datetime
import logging

import aiohttp
from aiohttp import web

from osmserver import osm, CONFIG_SECTION_OSMSERVER_OPTION_INTERVAL


async def handle_ws_request(request, **kwargs):
    """
    Handle requests received via the websocket.

    Args:
        request:
        **kwargs:

    """

    # setup the websocket
    websocket = web.WebSocketResponse()

    await websocket.prepare(request)

    async def module_state_sender(ws, **kwargs):
        """
        Routine to send the module state in a user-defined interval.

        Args:
            ws (web.WebSocketResponse): The websocket connection to use

        """
        while not ws.closed:
            state = await osm.module_states(**kwargs)

            await ws.send_json({'timestamp': datetime.datetime.now().isoformat(), 'enrichment': {**state}})

            await asyncio.sleep(float(kwargs[CONFIG_SECTION_OSMSERVER_OPTION_INTERVAL]))

    # run the module state sender routine
    asyncio.get_event_loop().create_task(module_state_sender(websocket, **kwargs))

    async for message in websocket:

        # process each message in the websocket
        if message.type == aiohttp.WSMsgType.TEXT:
            if message.data == 'close':
                await websocket.close()
            if message.data == 'state':
                state = await osm.module_states(**kwargs)

                await websocket.send_json({'timestamp': datetime.datetime.now().isoformat(), 'enrichment': {**state}})
            else:
                await websocket.send_str(message.data)


async def query_server(interpreter, request):
    """
    Query the local overpass server defined as ``interpreter`` with the ``request``.

    Args:
        interpreter (str): Path to the executable
        request (str): Request to query the server with.

    Returns:
        str: The query result

    """

    logging.info('Received request %s', request)

    # create a process
    proc = await asyncio.create_subprocess_shell(interpreter, stdin=asyncio.subprocess.PIPE,
                                                 stdout=asyncio.subprocess.PIPE)

    # send request to stdin of process
    stdout, stderr = await proc.communicate(request.encode())

    # wait until the process finished
    await proc.wait()

    # check return code of process
    return_code = proc.returncode

    logging.info('Interpreter result %d', proc.returncode)
    if stderr:
        logging.error('%s', stderr)

    if return_code is not None:
        result = bytes(stdout).decode()
    else:
        result = ''

    return return_code, result


async def handle_server_query_request(request, **kwargs):
    """
    Handle a client request for the overpass server.

    Args:
        request (web.Request): The HTTP request
    """
    logging.debug('Request received %s', request)
    # get the request data w.r.t the method
    try:
        if request.method == 'POST':
            data = await request.post()

            if 'data' not in data:
                data = await request.text()
            else:
                data = data.get('data')
        elif request.method == 'GET':
            data = request.query['data']
        else:
            data = None
    except KeyError:
        logging.error('The data field is not present')
        return web.HTTPBadRequest(reason='Missing required field "data".')

    if data is not None:
        return_code, osm_data = await query_server(kwargs['interpreter'], data)

        logging.debug('Return response\n%s', osm_data)

        return web.Response(text=osm_data,
                            content_type="application/json" if 'json' in data else "application/osm3s+xml")
    else:
        logging.error('Got an empty request')
        return web.HTTPBadRequest(reason='Got an empty request')
