"""Test webhooks integration with aiohttp web apps."""

# Standard library modules
import logging
import os

# Project modules
from custombot import Bot
from data.config import (
    local_host, local_port, log_file_name, errors_file_name,
    server_certificate, webhook_url
)
from data.passwords import appbot_token

if 1:
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


bot = Bot.get(
    token=appbot_token, webhook_url=webhook_url,
    certificate_path=server_certificate, local_host=local_host,
    local_port=local_port
)


@bot.command(command='/ping')
async def ping_command(update):
    """Send a pong when users `/ping`."""
    return "<i>Pong!</i>"


if __name__ == '__main__':
    Bot.run()
