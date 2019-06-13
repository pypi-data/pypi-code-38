import sys

import click

from tsfaker.exceptions import TsfakerException
from tsfaker.generator.table import TableGenerator
from tsfaker.utils.io import process_input_output, smart_open_write


@click.command(help="Generate a csv from table-schema descriptor(s),  "
                    "given as a local folder path, local files paths, remote url or on stdin ('-').")
@click.argument('schema_descriptors', type=str, nargs=-1)
@click.option('--output-files', '-o', default='-', type=str, multiple=True,
              help="Output files paths (same number as SCHEMAS_DESCRIPTORS) or stdout ('-' default), "
                   "or existing local folder path if SCHEMAS_DESCRIPTORS are given as a local folder path.")
@click.option('--nrows', '-n', default=10, type=int, help='Number of rows to generate (default=10).')
@click.option('--pretty', is_flag=True, help='Get a console-friendly tabular output, instead of csv.')
@click.option('--dry-run', is_flag=True, help='Write logs but do not generate data.')
def cli(schema_descriptors, output_files, nrows, pretty, dry_run):
    schema_descriptors, output_files = process_input_output(schema_descriptors, output_files)

    if not schema_descriptors:
        print('No input descriptor found')

    for descriptor, output in zip(schema_descriptors, output_files):
        print("Data generated from descriptor '{}' will be written on '{}'"
              .format('STDIN' if descriptor == sys.stdin else descriptor,
                      'STDOUT' if output == '-' else output))
        if dry_run:
            continue

        try:
            table_generator = TableGenerator(descriptor, nrows)
            table_string = table_generator.get_string(pretty)
        except TsfakerException as e:
            print(e.__class__, e)
            continue

        with smart_open_write(output) as f:
            f.write(table_string + '\n')


if __name__ == '__main__':
    cli()
