# -*- coding: utf-8 -*-
import asyncio
import json
import socket
import sys
import time
from urllib.error import URLError

import click

import click_spinner

import websockets
from websockets import WebSocketClientProtocol

from .. import cli
from .. import options
from ..api import Apps


@cli.cli.command()
@click.option('--follow', '-f', is_flag=True, help='Follow the logs')
@click.option('--last', '-n', default=10, help='Print the last n lines')
@click.option(
    '--services',
    '-s',
    'service',
    is_flag=True,
    help='Return logs from services used in the story',
)
@click.option(
    '--service-name',
    '-sn',
    default='*',
    help='Return logs for a specific service given by '
    'its name (eg: "redis" or "owner/name")',
)
@click.option(
    '--level',
    '-l',
    default='info',
    type=click.Choice(['debug', 'info', 'warning', 'error']),
    help='Specify the minimum log level '
    '(does not work when --services/-s is specified)',
)
@options.app()
def logs(follow, last, service, service_name, app, level):
    """
    Fetch logs for your app
    """
    cli.user()

    click.echo(f'Retrieving logs for {app}... ', nl=False)
    with click_spinner.spinner():
        app_id = Apps.get_uuid_from_hostname(app)

    click.echo()

    cli.track(
        'App Logs Requested',
        {
            'App name': app,
            'Follow': 'Yes' if follow else 'No',
            'Last N': last,
            'Source': 'Runtime' if service is False else 'Service',
            'Service Name': service_name if service else 'N/A',
            'Minimum level': level.capitalize(),
        },
    )

    asyncio.get_event_loop().run_until_complete(
        connect_and_listen_with_retry(
            app_id,
            last,
            follow,
            service is False,
            service,
            service_name,
            level,
        )
    )


async def ping_forever(websocket: WebSocketClientProtocol):
    while True:
        try:
            await websocket.send('{"command": "ping"}')
        except websockets.exceptions.ConnectionClosed:
            return  # Stop looping when this connection is closed.
        except URLError:
            return
        await asyncio.sleep(10)


async def connect_and_listen_with_retry(
    app_id, n, follow, runtime_logs, service_logs, service_name, level
):
    """
    Every 4-5 minutes, the connection terminates. This is
    not intentional, as the upstream server keeps it alive.
    However, something in the middle causes the connection to
    break. So, whenever it breaks, we just reconnect,
    but set N to be 0, since we want to continue from where we
    left off.
    If somebody does ever figure out why it breaks,
    please ping @judepereira on GitHub.
    """
    while True:
        try:
            completed = await connect_and_listen_once(
                app_id,
                n,
                follow,
                runtime_logs,
                service_logs,
                service_name,
                level,
            )
        except (URLError, socket.gaierror):
            click.echo('Network connection lost', err=True)
            sys.exit(1)
        except websockets.exceptions.InvalidStatusCode as e:
            if int(e.status_code / 100) == 5:
                click.echo(
                    'The upstream log server appears to be restarting.'
                    '\nPlease try again in a few seconds.',
                    err=True,
                )
            else:
                click.echo(
                    'The upstream log server did not respond.'
                    '\nPlease try again in a few seconds.',
                    err=True,
                )
            sys.exit(1)

        if completed:
            break

        # Don't worry, cut_off_ts will take care of
        # not printing duplicate messages.
        # We set n=100 just so that messages are not lost during a
        # connection termination.
        n = 100


cut_off_ts = 0
"""
Logic around cut_off_ts: This field holds the last last log's timestamp,
and is used to ensure that messages displayed by the CLI are not missed
in the event of an abrupt connection termination. See the pydoc for
connect_and_listen_with_retry above for more help.
"""


async def connect_and_listen_once(
    app_id, n, follow, runtime_logs, service_logs, service_name, level
):
    global cut_off_ts

    async with websockets.connect('wss://logs.storyscript.io') as websocket:
        assert isinstance(websocket, WebSocketClientProtocol)

        auth_payload = {
            'command': 'auth',
            'access_token': cli.get_access_token(),
            'id': cli.get_access_token(),
            'app_id': app_id,
        }
        await websocket.send(json.dumps(auth_payload))

        try:
            auth_response = await websocket.recv()

            # Generally, the log server will close the connection instantly.
            # This authorised check is just for consistency.
            # See https://github.com/storyscript/logstreamer#authentication.
            auth_response = json.loads(auth_response)
            if not auth_response['authorised']:
                raise websockets.exceptions.ConnectionClosed(-1, None)

        except websockets.exceptions.ConnectionClosed:
            click.echo(
                'The log server sent an unauthorised response.\n'
                'Are you sure you have access to view '
                'this app\'s logs?',
                err=True,
            )
            sys.exit(1)

        # Keep the connection alive by sending pings.
        asyncio.get_event_loop().create_task(ping_forever(websocket))

        # Send our filter payload.
        if runtime_logs:
            filter_payload = {
                'command': 'filter',
                'source': 'runtime',
                'level': level,
                'n': n,
                'watch': follow,
            }
        else:
            assert service_logs is True
            filter_payload = {
                'command': 'filter',
                'source': 'service',
                'service_name': service_name,
                'level': level,  # Note: The upstream server ignores level.
                'n': n,
                'watch': follow,
            }

        await websocket.send(json.dumps(filter_payload))

        last_log = None
        while True:
            try:
                message = await websocket.recv()
            except websockets.exceptions.ConnectionClosed:
                # Connection was closed since all the required log items were
                # sent.
                if not follow:
                    return True

                cut_off_ts = last_log['ts']
                return False

            log = json.loads(message)
            last_log = log

            if cut_off_ts >= log['ts']:
                continue

            date = time.strftime(
                '%b %d %H:%M:%S', time.localtime(int(log['ts'] / 1000))
            )

            tag = 'runtime'
            if service_logs:
                tag = log['service_name']

            colourize_and_print(date, tag, log['level'], log['message'])

    return True


def colourize_and_print(date, tag, level, message):
    level_col = 'green'  # Default for info.
    level = level.lower()
    if 'debug' in level:
        level_col = 'blue'
    elif 'warn' in level:
        level_col = 'yellow'
    elif 'crit' in level or 'error' in level:
        level_col = 'red'

    level = level[:7].rjust(7)
    tag = tag[:12].rjust(12)

    if tag:
        click.echo(
            f'{click.style(date, fg="white")} '
            f'{click.style(level.upper(), fg=level_col)} '
            f'{click.style(tag, fg="blue")}: '
            f'{message}'
        )
    else:
        click.echo(
            f'{click.style(date, fg="white")} '
            f'{click.style(level.upper(), fg=level_col)} '
            f'{message}'
        )
