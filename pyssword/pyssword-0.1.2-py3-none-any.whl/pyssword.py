import string
import secrets
import click

import util


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
ALPHABET = dict(
    nopunctuation=string.ascii_letters + string.digits,
    small=string.ascii_letters + string.digits + '!?@#$%&*+-_.,',
    full=string.ascii_letters + string.digits + string.punctuation,
)


@click.group(context_settings=CONTEXT_SETTINGS)
def main():
    pass


@main.command(options_metavar='<options>')
@click.argument('size', default=16, type=click.IntRange(10, None), metavar='<size>')
@click.option('-s', '--small', is_flag=True, help='Small set of valid punctuation symbols for password.')
@click.option('-n', '--nopunctuation', is_flag=True, help="Don't add punctuation symbols for password.")
@util.doc(
    f"""Make random passwords for given <size> and optionally chosen alphabet type.

    \b
    size:               Password length.
    alphabet type:
        default         {ALPHABET['full']}
        small           {ALPHABET['small']}
        nopunctuation   {ALPHABET['nopunctuation']}
    """
)
def run(**kwargs):
    if kwargs['nopunctuation']:
        alphabet = ALPHABET['nopunctuation']
    else:
        if kwargs['small']:
            alphabet = ALPHABET['small']
        else:
            alphabet = ALPHABET['full']

    while True:
        password = ''.join(secrets.choice(alphabet) for i in range(kwargs['size']))
        if (password[0] not in string.punctuation and (
            any(c in string.punctuation for c in password) or
                kwargs['nopunctuation']) and
            sum(c.islower() for c in password) >= 3 and
            sum(c.isupper() for c in password) >= 3 and
                sum(c.isdigit() for c in password) >= 3):
            print(password)
            break


if __name__ == '__main__':
    main()
