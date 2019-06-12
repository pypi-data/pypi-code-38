import click
import os
import re

from spell.cli.commands.keys import generate, get_remote_key
from spell.cli.commands.logout import logout
from spell.cli.log import logger
from spell.api.exceptions import UnauthorizedRequest
from spell.configs.config_handler import ConfigException
from spell.cli.exceptions import ExitException, api_client_exception_handler
from spell.cli.utils import add_known_host
from spell.cli.utils import cli_ssh_key_path


@click.command(name="login", short_help="Log in with your username or email")
@click.pass_context
@click.option("--identity", "identity",
              prompt="Enter your spell username or email",
              help="your registered spell username or email")
@click.password_option(prompt="Enter your spell password",
                       help="your registered spell password",
                       confirmation_prompt=False)
def login(ctx, identity, password):
    """
    Log in with your username or email.

    Prompts for the user's credentials and logs in to Spell. Both username and
    email are valid for login. If you don't have an account with Spell, please
    create one at https://spell.run.
    """
    config_handler = ctx.obj["config_handler"]
    config = config_handler.config

    # Log out existing session if it's for a different account
    if config:
        current_id = config.email if is_email(identity) else config.user_name
        if identity != current_id:
            try:
                ctx.invoke(logout, quiet=True)
            except Exception as e:
                logger.warning("Log out failed for previous session: %s", e)

    if config_handler.config is None:
        config_handler.load_default_config(type="global")

    config = config_handler.config
    client = ctx.obj["client"]

    with api_client_exception_handler():
        try:
            if is_email(identity):
                user, token = client.login_with_email(identity, password)
            else:
                user, token = client.login_with_username(identity, password)
        except UnauthorizedRequest as exception:
            raise ExitException(str(exception))

    logger.info("Sucessfully logged in.")
    config.token = token
    config.user_name = user.user_name
    config.email = user.email

    # If an owner is not configured, default to the organization (if any)
    if not config.owner and user.memberships and len(user.memberships) == 1:
        config.owner = user.memberships[0].organization.name

    try:
        config_handler.write()
    except ConfigException as e:
        raise ExitException(e.message)

    # Generate CLI key for user if one does not exist, or if the existing one
    # is not registered with the user's Spell account
    local_key = cli_ssh_key_path(config_handler)
    matching_remote_key = os.path.isfile(local_key) and get_remote_key(ctx, local_key)
    if not matching_remote_key:
        ctx.invoke(generate, force=True)

    # Attempt to add git.spell.run to known_hosts, ignore failures
    try:
        add_known_host("git.spell.run")
    except Exception:
        pass

    click.echo(u"Hello, {}!".format(user_addressing_noun(user)))


def is_email(input):
    return (re.match(".+@.+[.].+", input) is not None)


def user_addressing_noun(user):
    nouns = [user.full_name, user.user_name, user.email]
    return next((s for s in nouns if s), "")
