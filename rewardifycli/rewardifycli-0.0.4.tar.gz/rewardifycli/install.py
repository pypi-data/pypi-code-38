# third party
import click

# third party
from rewardify.env import EnvironmentInstaller

# local
from rewardifycli.util import Templater


@click.group(name='install')
def install():
    pass


@install.command('run')
@click.option('-p', '--path', 'path')
def run(path):
    templater: Templater = Templater.instance()

    installer = EnvironmentInstaller(path)
    installer.install()

    templater.echo_template('install.jinja2', {'path': path})

