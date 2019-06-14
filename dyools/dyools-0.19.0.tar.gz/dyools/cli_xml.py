from __future__ import (absolute_import, division, print_function, unicode_literals)

import sys

import click

from .klass_data import Data
from .klass_xml import Xml


@click.group(invoke_without_command=True)
@click.option('--attrs', '-a', type=click.STRING, nargs=2, multiple=True,
              help='Attributes with values like : \'name phone\' \'class text-left\'')
@click.option('--tags', '-t', type=click.STRING, nargs=1, multiple=True, help='Tags like \'div\' \'field\'')
@click.option('--separator', '-s', type=click.STRING, default=Xml.SEPARATOR,
              help='Use specific separator/delimiter to extract XML')
@click.option('--with-arch', is_flag=True, default=False, help='SHow also the XML architecture result')
def cli_xml(attrs, tags, separator, with_arch):
    """Xml query to export xpath and architecture"""
    attrs, tags = dict(attrs), list(tags)
    clean_arch = ''
    arch = ''
    for line in sys.stdin:
        arch += '\n{}'.format(line)
    if arch.count(separator) == 2:
        ok = False
        for line in arch.split('\n'):
            if line.strip() == separator.strip():
                if not ok:
                    ok = True
                    continue
                else:
                    break
            if ok:
                clean_arch += line + '\n'
    else:
        clean_arch = arch
    if with_arch:
        Data(Xml(clean_arch).expr_with_arch(*tags, **attrs)).show()
    else:
        Data(Xml(clean_arch).expr(*tags, **attrs)).show()
