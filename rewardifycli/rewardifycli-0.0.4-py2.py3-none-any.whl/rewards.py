# standard library
from collections import defaultdict

# third party
import click

from rewardify.main import Rewardify

# local
from rewardifycli.util import login_required
from rewardifycli.util import Templater, UserCredentials


@click.group(name='rewards')
def rewards():
    pass


@rewards.command('buy')
@click.argument('name')
@login_required
def buying(name):
    credentials: UserCredentials = UserCredentials.instance()
    facade: Rewardify = Rewardify.instance()
    templater: Templater = Templater.instance()
    username = credentials['username']

    context = {
        'name':         username,
        'cost':         '{} dust'.format(facade.CONFIG.REWARDS[name]['cost']),
        'balance':      '{} dust'.format(facade.user_get_dust(username))
    }

    try:
        facade.user_buy_reward(username, name)
        templater.echo_template('reward_bought.jinja2', context)
    except PermissionError:
        templater.echo_template('permission_buy_error.jinja2', context)
        raise click.Abort()


@rewards.command('use')
@click.argument('name')
@click.option('-a', '--all', 'all', is_flag=True)
@login_required
def using(name, all):
    credentials: UserCredentials = UserCredentials.instance()
    facade: Rewardify = Rewardify.instance()
    templater: Templater = Templater.instance()

    username = credentials['username']
    context = {
        'name':             name,
        'count':            1,
        'description':      facade.CONFIG.REWARDS[name]['description'],
    }

    try:
        if all:
            name_rewards_map = facade.user_get_rewards_by_name(username)
            reward_count = len(name_rewards_map[name])
            for i in range(reward_count):
                facade.user_use_reward(username, name)
            context.update({'count': reward_count})
        else:
            facade.user_use_reward(username, name)

        templater.echo_template('reward_used.jinja2', context)
    except LookupError:
        templater.echo_template('permission_use_error.jinja2', context)
    except Exception as e:
        click.echo(e)


@rewards.command('recycle')
@click.argument('name')
@login_required
def recycling(name):
    credentials: UserCredentials = UserCredentials.instance()
    facade: Rewardify = Rewardify.instance()
    templater: Templater = Templater.instance()
    username = credentials['username']

    context = {
        'name':         username,
        'recycle':      '{} dust'.format(facade.CONFIG.REWARDS[name]['recycle']),
    }

    try:
        facade.user_recycle_reward(username, name)
        templater.echo_template('reward_recycled.jinja2', context)
    except LookupError:
        templater.echo_template('permission_use_error.jinja2', context)
        raise click.Abort()


@rewards.command('list')
def listing():
    facade: Rewardify = Rewardify.instance()
    templater: Templater = Templater.instance()

    rarity_rewards_map = facade.available_rewards_by_rarity()
    context = defaultdict(list)
    context.update(rarity_rewards_map)

    templater.echo_template('reward_list.jinja2', context)
