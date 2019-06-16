# standard library
from collections import defaultdict

# third party
import click

from rewardify.main import Rewardify

# local
from rewardifycli.util import login_required
from rewardifycli.util import Templater, UserCredentials


@click.group(name='packs')
def packs():
    pass


@packs.command('buy')
@click.argument('name')
@login_required
def buy(name):
    credentials: UserCredentials = UserCredentials.instance()
    facade: Rewardify = Rewardify.instance()
    templater: Templater = Templater.instance()
    username = credentials['username']

    context = {
        'name':     username,
        'cost':     '{} gold'.format(facade.CONFIG.PACKS[name]['cost']),
        'balance':  '{} gold'.format(facade.user_get_gold(username))
    }

    try:
        facade.user_buy_pack(username, name)
        templater.echo_template('pack_bought.jinja2', context)
    except PermissionError:
        templater.echo_template('permission_buy_error.jinja2', context)
        raise click.Abort()


@packs.command('list')
def listing():
    facade: Rewardify = Rewardify.instance()
    templater: Templater = Templater.instance()

    available_packs = facade.available_packs()
    context = {'packs': available_packs}

    templater.echo_template('pack_list.jinja2', context)


@packs.command('open')
@click.option('-a', '--all', 'all', is_flag=True)
@click.argument('name')
@login_required
def opening(all, name):
    credentials: UserCredentials = UserCredentials.instance()
    facade: Rewardify = Rewardify.instance()
    templater: Templater = Templater.instance()

    username = credentials['username']
    context = {
        'name':         username,
        'count':        1,
    }
    name_rewards_map_before = defaultdict(list)
    name_rewards_map_before.update(facade.user_get_rewards_by_name(username))

    try:
        if all:
            name_pack_map = facade.user_get_packs_by_name(username)
            pack_count = len(name_pack_map[name])
            for i in range(pack_count):
                facade.user_open_pack(username, name)
            context.update({'count': pack_count})
        else:
            facade.user_open_pack(username, name)

        name_rewards_map_after = facade.user_get_rewards_by_name(username)

        rarity_rewards_map = defaultdict(list)
        for name, rewards in name_rewards_map_after.items():
            rewards_before = name_rewards_map_before[name]
            new_reward_count = len(rewards) - len(rewards_before)
            rarity = str(rewards[0].rarity)
            for i in range(new_reward_count):
                rarity_rewards_map[rarity].append(rewards[0])

        context.update(rarity_rewards_map)

        templater.echo_template('pack_opened.jinja2', context)
    except LookupError:
        templater.echo_template('permission_use_error.jinja2', context)
    except Exception as e:
        click.echo(e)
