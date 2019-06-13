import click
from alfa_sdk import SecretsClient
from alfa_cli.common.factories import create_session


@click.group()
@click.pass_context
def secrets(ctx):
    """Store and retrieve secrets in ALFA."""
    session = create_session()
    ctx.obj["client"] = SecretsClient(session=session)


#


@secrets.command()
@click.pass_obj
def get_names(obj):
    """Retrieve list of secrets"""
    res = obj["client"].get_names()
    return obj["logger"].result(res)


@secrets.command()
@click.argument("name", type=str)
@click.pass_obj
def get_value(obj, name):
    """Retrieve the value of a secret"""
    res = obj["client"].get_value(name)
    return obj["logger"].result(res)


@secrets.command()
@click.argument("name", type=str)
@click.argument("value", type=str)
@click.option("-d", "--description", type=str, help="Description of the secret", default=None)
@click.pass_obj
def put_value(obj, name, value, description):
    """Save/update the value of a secret"""
    res = obj["client"].put_value(name, value, description=description)
    return obj["logger"].result(res)


@secrets.command()
@click.argument("name", type=str)
@click.pass_obj
def delete_value(obj, name):
    """Delete a secret"""
    res = obj["client"].delete_value(name)
    return obj["logger"].result(res)

