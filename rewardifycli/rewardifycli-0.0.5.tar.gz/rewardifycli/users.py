# standard library
from collections import defaultdict

# third party
import click

from rewardify.main import Rewardify

# local
from rewardifycli.util import login_required
from rewardifycli.util import Templater, UserCredentials


@click.group(name='users')
def users():
    pass


@users.command('create')
@click.argument('username')
@click.argument('password')
def create(username, password):
    credentials: UserCredentials = UserCredentials.instance()
    facade: Rewardify = Rewardify.instance()
    templater: Templater = Templater.instance()

    context = {
        'username':     username,
    }

    try:
        facade.create_user(username, password)
        templater.echo_template('user_created.jinja2', context)
    except Exception as e:
        click.echo(e)
        raise click.Abort()
