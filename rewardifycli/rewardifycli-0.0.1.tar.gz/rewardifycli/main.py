# third party
import click

# local
from rewardifycli.install import install
from rewardifycli.packs import packs
from rewardifycli.rewards import rewards
from rewardifycli.inventory import inventory
from rewardifycli.users import users


@click.group(name='rewardify')
def cli():
    pass


cli.add_command(install)
cli.add_command(packs)
cli.add_command(rewards)
cli.add_command(inventory)
cli.add_command(users)


if __name__ == '__main__':
    cli()
