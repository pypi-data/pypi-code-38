"""Click command module."""
import os
import platform
import re
import sys
from pathlib import Path

import click
import arrow
from loguru import logger

from megalus.bash.commands import bash
from megalus.buildcmd.commands import build
from megalus.check.commands import check
from megalus.commands.commands import config, install
from megalus.compose.commands import restart, scale, up
from megalus.down.commands import down
from megalus.logscmd.commands import logs
from megalus.main import Megalus
from megalus.run.commands import run
from megalus.status.commands import status
from megalus.stop.commands import stop
from megalus.start.commands import start


@click.group()
@click.option('--config_file', envvar='MEGALUS_PROJECT_CONFIG_FILE', required=True, type=click.Path())
@click.pass_context
def cli(ctx, config_file) -> None:
    """Define base click client.

    :param ctx: object: click context
    :param config_file: string: --config-file option
    :return: None
    """
    BASE_LOG_PATH = os.path.join(str(Path.home()), '.megalus', 'logscmd')

    if not os.path.exists(BASE_LOG_PATH):
        os.makedirs(BASE_LOG_PATH)

    now = arrow.utcnow().to("local").isoformat()
    LOGFILE = os.path.join(BASE_LOG_PATH, '{}.log'.format(now))
    if "windows" in platform.system().lower():
        LOGFILE = "".join(re.findall("[0-9]+", now))

    DEFAULT_LOGGER_MESSAGE = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> |" \
                             " <level>{level: <8}</level> - <level>{message}</level>"

    config = {
        "handlers": [
            {"sink": sys.stdout, "format": DEFAULT_LOGGER_MESSAGE},
            {"sink": LOGFILE, "retention": "7 days", "format": DEFAULT_LOGGER_MESSAGE}
        ],
    }
    logger.configure(**config)
    meg = Megalus(config_file=config_file, logfile=LOGFILE)
    meg.get_services()
    ctx.obj = meg


cli.add_command(bash)
cli.add_command(build)
cli.add_command(config)
cli.add_command(down)
cli.add_command(install)
cli.add_command(logs)
cli.add_command(restart)
cli.add_command(run)
cli.add_command(scale)
cli.add_command(stop)
cli.add_command(up)
cli.add_command(check)
cli.add_command(status)
cli.add_command(start)


def start() -> None:
    """Start command.

    :return: None
    """
    cli()
