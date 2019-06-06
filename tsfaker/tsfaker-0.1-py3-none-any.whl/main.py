import click

from tsfaker.generator.table import TableGenerator


@click.command(help='Generate a csv from a table-schema descriptor, given as a string, a file path or an url.')
@click.argument('table_schema', type=str)
@click.option('--nrows', default=10, type=int, help='Number of rows to generate')
def cli(table_schema, nrows):
    table_generator = TableGenerator(table_schema, nrows)
    print(table_generator.get_string())


if __name__ == '__main__':
    cli()
