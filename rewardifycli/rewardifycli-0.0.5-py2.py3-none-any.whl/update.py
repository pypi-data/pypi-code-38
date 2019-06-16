# standard library
from collections import defaultdict

# third party
import click

from rewardify.main import Rewardify

# local
from rewardifycli.util import login_required
from rewardifycli.util import Templater, UserCredentials


@click.command('update')
@login_required
def update():
    credentials: UserCredentials = UserCredentials.instance()
    facade: Rewardify = Rewardify.instance()
    templater: Templater = Templater.instance()

    context = {
        'backend':      facade.CONFIG.BACKEND
    }
    facade.backend_update()
    templater.echo_template('updated.jinja2', context)
