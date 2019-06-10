import click

from spell.cli.exceptions import (
    api_client_exception_handler,
    ExitException
)


@click.command(name="passwd", short_help="Set a new password for your Spell account")
@click.pass_context
def passwd(ctx, write=True):
    """
    Set a new password for your Spell account.

    Prompts for the user's current password before allowing the user to
    specify a new password.
    """
    client = ctx.obj["client"]
    old_password = click.prompt("Current spell password", hide_input=True)
    with api_client_exception_handler():
        client.check_password(old_password)

    new_password = click.prompt("Enter new spell password", hide_input=True)
    new_password_1 = click.prompt("Retype new spell password", hide_input=True)
    if new_password != new_password_1:
        raise ExitException("New passwords don't match")

    with api_client_exception_handler():
        client.change_password(old_password, new_password)

    click.echo("Password changed successfully!")
