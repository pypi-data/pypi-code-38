# -*- coding: utf-8 -*-
import click

from spell.cli.exceptions import api_client_exception_handler, ExitException


@click.command(name="owner", hidden=True)
@click.argument("name", required=False)
@click.pass_context
def owner(ctx, name):
    """
    Displays, and optionally selects, owners that the user can interact with.
    """
    # Owner the CLI is currently configured to use
    current_owner = ctx.obj["owner"]

    # Generate the list of possible owners for the user
    with api_client_exception_handler():
        user = ctx.obj["client"].get_user_info()
    possible_owners = [user.user_name]
    if user.memberships:
        possible_owners.extend([m.organization.name for m in user.memberships])

    # Configure CLI to use a different owner
    if name and name != current_owner:
        if name not in possible_owners:
            raise ExitException("Invalid owner name: " + name)
        config_handler = ctx.obj["config_handler"]
        current_owner = ctx.obj["owner"] = config_handler.config.owner = name
        config_handler.write()

    # Display list of owners with the current one highlighted
    for owner in possible_owners:
        if owner == current_owner:
            prefix = u"➔ " if ctx.obj["utf8"] else "* "
            click.echo(prefix + click.style(owner, fg="green"))
        else:
            click.echo("  " + owner)
