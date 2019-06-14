from __future__ import (absolute_import, division, print_function, unicode_literals)

import os

import click
import polib

from .klass_path import Path
from .klass_print import Print
from .klass_yaml_config import YamlConfig

DATABASE_PATH = Path.create_dir(os.path.join(Path.home(), '.dyvz', 'po_databases'))


@click.group()
def cli_po():
    """Translations: create a database and translate po files"""
    pass


@cli_po.command('update_db')
@click.argument('path', type=click.STRING, required=True)
@click.option('--lang', type=click.STRING, default='fr', required=True, help='The code of the language, default=fr')
def __update_database(path, lang):
    """Update the translation database from a directory or a file"""
    global DATABASE_PATH
    if os.path.isfile(path):
        files = [path]
    elif os.path.isdir(path):
        files = Path.find_files(expr='{}.po'.format(lang), path=path)
    else:
        raise FileNotFoundError('The path [%s] not found' % path)
    DATABASE_PATH = os.path.join(DATABASE_PATH, '{}.yml'.format(lang))
    yaml = YamlConfig(DATABASE_PATH, create_if_not_exists=True)
    db = yaml.get_data()
    for f in files:
        po = polib.pofile(f, encoding='utf-8')
        for entry in po:
            db.update({entry.msgid: entry.msgstr})
    yaml.dump()


@cli_po.command('translate')
@click.argument('path',
                type=click.Path(
                    exists=True,
                    file_okay=True,
                    dir_okay=False,
                    writable=True,
                    readable=True,
                    resolve_path=True
                ),
                )
@click.argument('lang', type=click.STRING, default='fr', required=True)
@click.option('--untranslated', is_flag=True, type=click.BOOL, default=False, required=False,
              help='Translate only untranslated terms', )
def __translate(path, lang, untranslated):
    """Fill a po file"""
    global DATABASE_PATH
    DATABASE_PATH = os.path.join(DATABASE_PATH, '{}.yml'.format(lang))
    if os.path.isfile(DATABASE_PATH):
        yaml = YamlConfig(DATABASE_PATH)
        db = yaml.get_data()
    else:
        Print.warning('please initialize a database with command: po update_db PATH')
        db = {}
    po = polib.pofile(path, encoding='utf-8')
    for entry in po:
        if untranslated and entry.msgstr:
            continue
        default = entry.msgstr or db.get(entry.msgid, '')
        value = click.prompt('{}% - {}'.format(po.percent_translated(), entry.msgid), default)
        entry.msgstr = value
    po.save(path)
    Print.success('{}% - Translation is finished'.format(po.percent_translated()))
