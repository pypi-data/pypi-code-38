from importlib import import_module
from os import getcwd
from pprint import pprint

import click
import sys
from click import ClickException

from pyqalx import Bot, QalxSession


@click.group(chain=True)
@click.option(
    '-u', '--user-profile',
    help='User profile name in .qalx.',
    default="default"
)
@click.option(
    '-b', '--bot-profile',
    help='Bot profile name in .bots.',
    default="default"
)
@click.pass_context
def qalx(ctx, user_profile, bot_profile):
    """Command line interface to qalx."""
    ctx.ensure_object(dict)
    ctx.obj['USER_PROFILE'] = user_profile
    ctx.obj['BOT_PROFILE'] = bot_profile
    sys.path.append(getcwd())


@qalx.command("start-bot")
@click.option(
    '-p', '--processes',
    help='The number of workers to spawn in the bot.',
    default=1
)
@click.argument("target")
@click.pass_context
def start(ctx, target, processes):
    """
    start the bot at TARGET.

    This is the import path with a colon followed by the variable name of the bot. e.g. `my_qalx.my_bot:bot`
    """
    bot_module_name, bot_variable_name = target.split(":")
    bot_module = import_module(bot_module_name)
    if bot_variable_name not in dir(bot_module):
        raise ClickException(f"{bot_variable_name} not found in {bot_module_name}.")
    else:
        bot = getattr(bot_module, bot_variable_name)
        if not isinstance(bot, Bot):
            raise ClickException(f"{bot_variable_name} isn't an instance of Bot.")
        click.echo(f"Starting {bot.name} reading from {bot.queue_name} with"
                   f" {processes} workers.")
        user_profile = ctx.obj.get("USER_PROFILE", "default")
        bot_profile = ctx.obj.get("BOT_PROFILE", "default")
        bot.start(user_profile_name=user_profile,
                  bot_profile_name=bot_profile,
                  processes=int(processes))


@qalx.command("terminate-bot")
@click.argument("name")
@click.pass_context
def terminate_bot(ctx, name):
    """shutdown the bot named NAME"""
    qalx_session = QalxSession(profile_name=ctx.obj.get("USER_PROFILE", "default"))
    bot_to_kill = qalx_session.bot.find_one(name=name)
    qalx_session.bot.terminate(bot_to_kill)
    click.echo(f"Terminated {name}")


@qalx.command("stop-bot")
@click.argument("name")
@click.pass_context
def stop_bot(ctx, name):
    """stop the bot named NAME.

    All workers to stop pulling jobs from the queue.
    """
    qalx_session = QalxSession(profile_name=ctx.obj.get("USER_PROFILE", "default"))
    bot_to_stop = qalx_session.bot.find_one(name=name)
    qalx_session.bot.stop(bot_to_stop)
    click.echo(f"Stopping {name}.")


@qalx.command("resume-bot")
@click.argument("name")
@click.pass_context
def resume_bot(ctx, name):
    """resume the bot named NAME.

    All workers to start pulling jobs from the queue.
    """
    qalx_session = QalxSession(profile_name=ctx.obj.get("USER_PROFILE", "default"))
    bot_to_resume = qalx_session.bot.find_one(name=name)
    qalx_session.bot.resume(bot_to_resume)
    click.echo(f"Resuming {name}.")


@qalx.command("bot-info")
@click.argument("name")
@click.pass_context
def bot_info(ctx, name):
    """print info about the bot named NAME.

    """
    qalx_session = QalxSession(profile_name=ctx.obj.get("USER_PROFILE", "default"))
    bot_to_info = qalx_session.bot.find_one(name=name)
    click.echo(pprint(bot_to_info))


@qalx.command("terminate-workers")
@click.argument("bot_name")
@click.argument("number")
@click.pass_context
def terminate_workers(ctx, bot_name, number):
    """terminate NUMBER of workers on bot named BOT_NAME."""
    qalx_session = QalxSession(profile_name=ctx.obj.get("USER_PROFILE", "default"))
    bot_to_kill = qalx_session.bot.find_one(name=bot_name)
    if int(number) > len(bot_to_kill['workers']):
        raise ClickException(
            f"{number} is more than the number of workers on {bot_name} ({len(bot_to_kill['workers'])})")
    for n in range(int(number)):
        qalx_session.worker.terminate(bot_to_kill['workers'][n], bot_entity=bot_to_kill)
        click.echo(f"Terminated {n + 1} worker.")
