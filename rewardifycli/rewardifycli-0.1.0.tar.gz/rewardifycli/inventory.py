# standard library
from collections import defaultdict

# third party
import click

from rewardify.main import Rewardify

# local
from rewardifycli.util import login_required
from rewardifycli.util import Templater, UserCredentials


@click.command('inventory')
@login_required
def inventory():
    credentials: UserCredentials = UserCredentials.instance()
    facade: Rewardify = Rewardify.instance()
    templater: Templater = Templater.instance()
    username = credentials['username']

    context = {
        'name':         username,
        'dust':         facade.user_get_dust(username),
        'gold':         facade.user_get_gold(username),
        'rewards':      facade.user_get_rewards_by_name(username),
        'packs':        facade.user_get_packs_by_name(username)
    }

    templater.echo_template('inventory.jinja2', context)
