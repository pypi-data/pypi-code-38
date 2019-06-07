import json
import logging
import sys

import click

from opendataschema import GitTableSchemaReference, TableSchemaCatalog


def print_json(data):
    click.echo(json.dumps(data, indent=2, sort_keys=True))


@click.group()
@click.option('--catalog', help='schema catalog file')
@click.option('--log', default="info", help='logging level')
@click.pass_context
def cli(ctx, catalog, log):
    numeric_level = getattr(logging, log.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: {}'.format(log))
    logging.basicConfig(
        format="%(levelname)s:%(name)s:%(asctime)s:%(message)s",
        level=numeric_level,
        stream=sys.stdout,  # Use stderr if script outputs data to stdout.
    )
    ctx.obj = {"catalog": TableSchemaCatalog(catalog)}


@cli.command()
@click.pass_context
def list(ctx):
    catalog = ctx.obj["catalog"]
    click.echo("\n".join(sorted(catalog.references.keys())))


@cli.command()
@click.option("--name", help="show this schema")
@click.option("--versions/--no-versions", default=False, help="also show versions for schemas referenced as Git repositories")
@click.pass_context
def show(ctx, name, versions):
    catalog = ctx.obj["catalog"]
    if name:
        reference = catalog.references.get(name)
        if not reference:
            click.echo("Unknown schema \"{}\"".format(name))
            ctx.exit(1)
        print_json(reference.to_json())
    else:
        print_json({k: v.to_json(versions=versions) for k, v in catalog.references.items()})


if __name__ == '__main__':
    cli()  # pylint: disable=no-value-for-parameter
