import click
import json
from .base_schema import dict2schemas


@click.command()
@click.option('--jsonfile', default=None)
@click.option('--name', default='data')
def json2schemas(jsonfile, name):
    with open(jsonfile, 'r') as f:
        values = f.read()
        print('\n' + dict2schemas(json.loads(values.strip()), name).code_gen())  # NOQA
