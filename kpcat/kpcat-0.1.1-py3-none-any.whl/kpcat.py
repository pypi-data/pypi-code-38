import inspect
import json
from typing import Dict

import click
import construct
from pykeepass import PyKeePass, pykeepass

JSON_OUTPUT_FORMAT = 'json'
TEXT_OUTPUT_FORMAT = 'text'
OUTPUT_FORMATS = [JSON_OUTPUT_FORMAT, TEXT_OUTPUT_FORMAT]
DEFAULT_OUTPUT_FORMAT = TEXT_OUTPUT_FORMAT


@click.command('kpcat')
@click.argument('KEEPASS_FILE', type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option('--password', prompt=True, hide_input=True, envvar='KPCAT_PASSWORD',
              help='Password for keepass file. Will try to load $KPCAT_PASSWORD from the environment first, '
                   'which can be overriden by this option. If neither are supplied a prompt will ask for your password. '
                   'NOTE: using a prompt will not work if piping the output to another command.')
@click.option('--keyfile', type=click.Path(exists=True, file_okay=True, dir_okay=False),
              help='Key file for keepass file.')
@click.option('--show-passwords', is_flag=True, help='Option to show passwords in output; passwords are '
                                                     'redacted by default.')
@click.option('--output-format', type=click.Choice(OUTPUT_FORMATS), default=DEFAULT_OUTPUT_FORMAT,
              help='Format type for output. Default: {}'.format(DEFAULT_OUTPUT_FORMAT))
def main(keepass_file, password, keyfile, show_passwords, output_format):
    """
    cat a keepass file
    """
    try:
        kp = PyKeePass(keepass_file, password=password, keyfile=keyfile)
    except construct.core.ChecksumError:
        raise click.ClickException('Incorrect password')

    entries = kp.entries  # TODO: implement a filter?
    for i, entry in enumerate(entries):
        entry_as_dict = _get_entry_as_dict(entry, show_passwords=show_passwords)
        if output_format == JSON_OUTPUT_FORMAT:
            click.echo(json.dumps(entry_as_dict))
        elif output_format == TEXT_OUTPUT_FORMAT:
            click.echo(_dict_to_text(entry_as_dict))
        else:
            raise Exception('Bad output format; there be a bug')


def _get_entry_as_dict(entry: pykeepass.Entry,
                       *,
                       show_passwords: bool = False) -> Dict[str, str]:
    props = [x for x in dir(entry)
             if not x.startswith('_')
             and not inspect.ismethod(getattr(entry, x))]

    result = {}
    for prop in props:
        value = getattr(entry, prop)
        if prop == 'password' and not show_passwords:
            value = 'REDACTED'

        if type(value) == pykeepass.Group:
            value = value.name

        result[prop] = str(value)
    return result


def _dict_to_text(props: Dict[str, str],
                  *,
                  single_line: bool = True) -> str:
    result = ''
    for prop in sorted(props):
        value = props[prop]
        if single_line:
            value = value.replace('\n', '')
        result += '{}: {}'.format(prop, value)

        if not single_line:
            result += '\n'
        else:
            result += ' '

    if result[-1] == '\n':  # strip off the last new line
        result = result[:-1]

    return result


if __name__ == '__main__':
    main()
