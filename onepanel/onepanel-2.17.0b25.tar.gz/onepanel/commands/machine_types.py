"""
Machine types commands
"""

import click

from onepanel.commands.base import APIViewController
from onepanel.commands.login import login_required


class MachineTypesViewController(APIViewController):

    def __init__(self,conn):
        APIViewController.__init__(self,conn)


@click.group(name='machine-types', help='Machine type commands')
@click.pass_context
def machine_types(ctx):
    ctx.obj['vc'] = MachineTypesViewController(ctx.obj['connection'])


@machine_types.command('list', help='Show a list of available machine types')
@click.pass_context
@login_required
def list_machine_types(ctx):
    vc = ctx.obj['vc']
    print_data = vc.list(params="/machine_types")
    fields = ['uid','name']
    field_names = ['UID','SPECS']
    empty_message = 'No available machine types.'
    vc.print_items(print_data,fields,field_names,empty_message)

