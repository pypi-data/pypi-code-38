import click, sys
from polysecrets.main import PolySecrets
from polysecrets.version import __version__


@click.command()
@click.option('-s', '--secret', required=1, type=click.STRING, help='The secret string')
@click.option('-l', '--length', default=10, type=click.INT, help='Length of the secret. Secret has a minimum length '
                                                                 'of 10')
@click.option('-u', '--uuid', default=True, type=click.INT, help='Whether to use UUIDs or Alphanumeric characters for '
                                                                 'secret generation')
@click.option('-m', '--mixcase', default=False, type=click.BOOL, help='Decide whether or not to mix the case of alpha'
                                                                      'characters in secret string')
@click.version_option(version=__version__)
def cli(secret, length, uuid, mixcase):
    if not isinstance(uuid, int):
        print(f'UUID must be a integer of 0, 1, or 2. You have {uuid}, which is invalid.')
        sys.exit()
    else:
        print('Secret: ', PolySecrets(secret, length=length, uuids=uuid, mix_case=mixcase).manual())
        sys.exit()


if __name__ == '__main__':
    try:
        cli()
    except (AttributeError, AssertionError, Exception) as excep:
        print(f'Fatal error - {excep}')
        sys.exit(1)
