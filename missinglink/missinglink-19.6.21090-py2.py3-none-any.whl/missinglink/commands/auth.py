# -*- coding: utf-8 -*-
import os

import click
from terminaltables import PorcelainTable

from missinglink.commands.commons import print_as_json
from missinglink.core.api import ApiCaller
from missinglink.commands.utilities.options import CommonOptions
from missinglink.commands.utilities.tables import dict_to_csv
from .commons import output_result


@click.group('auth', help='Authorization Commands.')
def auth_commands():
    pass


@auth_commands.command('init')
@click.pass_context
@click.option('--webserver/--disable-webserver', default=True, required=False, help='Enables or disables the webserver')
def init_auth(ctx, webserver):
    """Authenticates the CLI."""
    from .commons import pixy_flow

    ctx.obj.local_web_server = webserver

    access_token, refresh_token, id_token = pixy_flow(ctx.obj)

    ctx.obj.config.update_and_save({
        'token': {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'id_token': id_token,
        }
    })


@auth_commands.command('whoami')
@click.pass_context
def whoami(ctx):
    """Displays the info of the current user."""
    token_data = ctx.obj.config.token_data

    result = {
        'user_id': token_data.get('uid'),
        'name': token_data.get('name'),
        'email': token_data.get('email'),
    }
    json_format = ctx.obj.output_format == 'json'
    format_tables = not json_format

    if format_tables:
        fields = ['name', 'email', 'user_id']
        table_data = list(dict_to_csv(result, fields))

        click.echo(PorcelainTable(table_data).table)
    else:
        print_as_json(result)


@auth_commands.command('resource')
@CommonOptions.org_option()
@click.pass_context
def auth_resource(ctx, org):
    """Creates a service token for a specific resource."""
    result = ApiCaller.call(ctx.obj, ctx.obj.session, 'get', '{org}/resource/authorise'.format(org=org))

    output_result(ctx, result, ['token'])


@auth_commands.command('debug-local', hidden=True)
@click.pass_context
def init_auth(ctx):
    from jinja2 import Template
    template = Template(open(os.path.join(os.path.dirname(__file__), 'templates', 'debug_dm.py')).read())

    config = ctx.obj.config
    token_data = config.token_data
    user_id = token_data.get('uid')
    click.echo(template.render(refresh_token=config.refresh_token, user_id=user_id, api_host=config.api_host))
