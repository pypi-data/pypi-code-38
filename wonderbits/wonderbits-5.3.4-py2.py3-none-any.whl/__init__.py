from .core import *

import click
from wonderbits import wb_tool

@click.command()
@click.option('--file', default='', help='absolute path')
def upload(file):
    wb_tool.upload.upload_with_file_path(file)
    click.echo("Hello {}!".format(file))

# if __name__ == '__main__':
#     upload()