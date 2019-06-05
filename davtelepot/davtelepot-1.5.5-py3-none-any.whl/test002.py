"""Test webhooks integration with aiohttp web apps."""

# Standard library modules
import asyncio
import logging
import os

# Third party modules
from aiohttp import web
from telepot.aio.loop import OrderedWebhook

# Project modules
from data.config import (
    local_host, local_port, log_file_name, errors_file_name,
    server_certificate, webhook_url
)
from data.passwords import appbot_token
from sitebot import Bot

path = os.path.dirname(__file__)
log_file = "{}/data/{}".format(path, log_file_name)
errors_file = "{}/data/{}".format(path, errors_file_name)

# Outputs the log in console, log_file and errors_file
# Log formatter: datetime, module name (filled with spaces up to 15
# characters), logging level name (filled to 8), message
log_formatter = logging.Formatter(
    "%(asctime)s [%(module)-15s %(levelname)-8s]     %(message)s",
    style='%'
)
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.DEBUG)
root_logger.addHandler(file_handler)

file_handler = logging.FileHandler(errors_file, mode="a", encoding="utf-8")
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.ERROR)
root_logger.addHandler(file_handler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(log_formatter)
consoleHandler.setLevel(logging.DEBUG)
root_logger.addHandler(consoleHandler)


async def feeder(request):
    """Handle incoming HTTP `request`s.

    Get data, feed webhook and return and OK message.
    """
    data = await request.text()
    webhook.feed(data)
    return web.Response(
        body='OK'.encode('utf-8')
    )


async def test(request):
    """Print `request` and return an OK response."""
    print(request)
    return web.Response(
        text='OK! =)'
    )


async def start_bot_webhook(app, bot, certificate):
    """Add route for webhook and set webhook for Telegram."""
    app.router.add_route('GET', '/davtetest/webhook/test', test)
    app.router.add_route('GET', '/davtetest/webhook', feeder)
    app.router.add_route('POST', '/davtetest/webhook', feeder)
    # Do not start until bot has got information about itself
    await bot.get_me()
    with open(certificate, 'r') as _certificate:
        await bot.setWebhook(webhook_url, certificate=_certificate)


loop = asyncio.get_event_loop()
app = web.Application(loop=loop)
bot = Bot(token=appbot_token)


@bot.command(command='/ping')
async def ping_command(update):
    """Send a pong when users `/ping`."""
    return "<i>Pong!</i>"


webhook = OrderedWebhook(bot)


if __name__ == '__main__':
    loop.run_until_complete(
        start_bot_webhook(app, bot, server_certificate)
    )
    loop.create_task(
        webhook.run_forever()
    )
    try:
        web.run_app(app, host=local_host, port=local_port)
    except KeyboardInterrupt:
        pass
