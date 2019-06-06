import click
import logging

from regindexer.indexer import Indexer


@click.group()
@click.option('-c', '--config', metavar='CONFIG_FILE',
              help='Path to config file',
              default='/etc/regindexer/config.yaml')
@click.option('-v', '--verbose', is_flag=True,
              help='Show verbose debugging output')
@click.pass_context
def cli(ctx, config, verbose):
    ctx.obj = {
        'config': config
    }

    if verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)


@cli.command(name="index")
@click.pass_context
def index(ctx):
    """Rebuild indexes"""
    indexer = Indexer(config=ctx.obj['config'])
    indexer.index()
