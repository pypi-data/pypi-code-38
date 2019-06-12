import click
import logging

from .api import Client
from .sql import SQLCache
from .file import FileCache


class Container:
    pass


@click.group()
@click.option('-l', '--log-level', envvar="PPC_LOG", default="INFO")
@click.option('-u', '--username', envvar='PPC_USR', help="RedLock Username")
@click.option('-p', '--password', envvar='PPC_PWD', help="RedLock Password")
@click.option('-e', '--endpoint', envvar='PPC_URL', default="https://api.redlock.io/", help="RedLock API Endpoint URL")
@click.option('-d', '--database', envvar='PPC_DB', default="ppc.db", help="Sqlite3 database filename for cache")
@click.option('-c', '--cache-dir', envvar='PPC_CD', default="ppccache/", help="Dirname for file cache")
@click.pass_context
def cli(ctx, log_level, username, password, endpoint, database, cache_dir):
    """ppc is a collection of tools to interact with Prisma Public Cloud(formerly RedLock). Mainly
    created to interact with Policies and RQL"""
    level = log_level.upper()
    if level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
        raise Exception("Bad Log Level")

    logging.getLogger().setLevel(level)
    logging.debug(f"Logging set to {level}")

    my_obj = Container()
    my_obj.c = Client(username, password, endpoint)
    #my_obj.db = SQLCache(database, my_obj.c)
    #my_obj.fs = FileCache(cache_dir, my_obj.c)

    ctx.obj = my_obj


@cli.command()
@click.pass_obj
def dump_policies_to_db(obj):
    policies = obj.c.policies
    for policy in policies:
        print(policy)

    print(len(policies))
    print(dir(policies.head()))


@cli.command()
@click.pass_obj
def get_token(obj):
    """Logs in and returns a JWT. Good for exploring api via curl or api docs if needed."""
    click.echo(obj.c.token)

@cli.command()
@click.pass_obj
def dump_policies(obj):
    """Gets the Policies json array from the API"""
    click.echo(obj.c.policies.json)

@cli.command()
@click.pass_obj
def dump_alerts(obj):
    """Gets the Alerts json array from the API"""
    click.echo(obj.c.alerts.json)

@cli.command()
@click.pass_obj
def dump_criteria(obj):
    """Gets the Criteria json array from the API"""
    click.echo(obj.c.criteria.json)

