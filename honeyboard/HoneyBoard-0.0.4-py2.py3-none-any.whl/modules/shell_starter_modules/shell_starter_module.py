from honey_board.models.settings import config
import click
import honey_board.modules.shell_starter_modules.shell_starter_net_state_module as ns_module
import honey_board.modules.shell_starter_modules.shell_starter_general_module as general_module

#create all command line groups
cli = click.CommandCollection(
    sources=
    [
        general_module.general_commands_cli,
        ns_module.net_stats_commands_cli
    ]
)
