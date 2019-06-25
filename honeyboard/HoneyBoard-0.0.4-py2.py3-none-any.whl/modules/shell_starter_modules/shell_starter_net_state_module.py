import click
import honey_board.modules.net_state_modules.net_state_module as ns_module
import logging

#network stats group for click
@click.group()
def net_stats_commands_cli():
    pass

#get network state
@net_stats_commands_cli.command()
def get_net_state():
    try:
        logging.info("Get network state")
        click.echo(ns_module.get_net_state_info())
    except Exception as e:
        logging.error("Error. "+str(e))
