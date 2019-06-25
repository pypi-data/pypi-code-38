from models.settings import config
import click
import modules.shell_starter_modules.shell_starter_net_state_module as ns_module
import modules.shell_starter_modules.shell_starter_general_module as general_module

#create all command line groups
cli = click.CommandCollection(
    sources=
    [
        general_module.general_commands_cli,
        ns_module.net_stats_commands_cli
    ]
)
