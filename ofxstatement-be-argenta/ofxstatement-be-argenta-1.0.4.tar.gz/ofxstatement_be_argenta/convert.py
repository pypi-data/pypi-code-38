#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import click
import logging

from ofxstatement.ofx import OfxWriter
from ofxstatement.plugins import argenta

@click.command()
@click.argument('path', type=click.Path(exists=True, readable=True))
@click.option('--debug', is_flag=True, default=False, 
    help='Log assertions and statement lines. No file is written.')
def convert(path, debug):
    """Parse and write transactions from Argenta_iban_date.xlsx file. The given file is renamed."""

    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level, format='[%(levelname)s] %(message)s')

    with argenta.ArgentaPlugin(ui=None, settings=None).get_parser(path) as parser:
        statement = parser.parse()
        logging.debug('Statement has been parsed.')

    if debug:
        logging.debug('Statement.lines:')
        for line in statement.lines:
            print(line)
        return
    
    date_suffix = statement.lines[-1].date.strftime("-%y%m%d")
    ext = os.path.splitext(path)[1]
    dir = os.path.dirname(path)
    base_filename = os.path.join(dir, statement.account_id + date_suffix)
    output_file = base_filename + '.ofx'

    with open(output_file, 'w') as out:
        writer = OfxWriter(statement)
        out.write(writer.toxml())
        logging.info('Statement has been written to ' + output_file)
        
    path_new = base_filename + ext
    os.rename(path, path_new)
    logging.info('Original file has been renamed to ' + path_new)

if __name__ == '__main__':
    convert()
