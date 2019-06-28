import click
import json
from .base_schema import dict2schemas


@click.command()
@click.option('--jsonfile', default=None)
@click.option('--name', default='data')
@click.option('--dump', default=False)
@click.option('--load', default=False)
def json2schemas(jsonfile, name, dump, load):
    with open(jsonfile, 'r') as f:
        values = f.read()
        print('\n' + dict2schemas(  # NOQA
            json.loads(values.strip()), name, dump=dump, load=load).code_gen())  # NOQA
