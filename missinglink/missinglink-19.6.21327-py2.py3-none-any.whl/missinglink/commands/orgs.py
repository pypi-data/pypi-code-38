# -*- coding: utf-8 -*-
from functools import wraps

import click
from missinglink.core.api import ApiCaller

from missinglink.commands.utilities.options import CommonOptions
from .commons import add_to_data_if_not_none, output_result

ORG_MEMBER_TABLE_HEADERS = ['user_id', 'email', 'first_name', 'last_name']


@click.group('orgs', help='Organization Management Commands.')
def orgs_commands():
    pass


@orgs_commands.command('list')
@click.pass_context
def list_orgs(ctx):
    """Lists organizations attached to the authenticated user."""
    result = ApiCaller.call(ctx.obj, ctx.obj.session, 'get', 'orgs')

    output_result(ctx, result.get('orgs', []), ['org', 'display_name'])


@orgs_commands.command('create')
@CommonOptions.org_option()
@CommonOptions.display_name_option(required=False)
@CommonOptions.description_option()
@click.pass_context
def create_org(ctx, org, display_name, description):
    """Create new organization.
    Creates a new organization and attaches is to the authenticated user."""
    data = {}

    add_to_data_if_not_none(data, display_name, 'display_name')
    add_to_data_if_not_none(data, description, 'description')
    add_to_data_if_not_none(data, org, 'org')

    result = ApiCaller.call(ctx.obj, ctx.obj.session, 'post', 'orgs', data)

    output_result(ctx, result, ['ok'])


@orgs_commands.command('members')
@CommonOptions.org_option()
@click.pass_context
def org_members(ctx, org):
    """Lists the members in the specified organization."""
    result = ApiCaller.call(ctx.obj, ctx.obj.session, 'get', 'orgs/{org}/members'.format(org=org))

    output_result(ctx, result.get('members', []), ORG_MEMBER_TABLE_HEADERS)


@orgs_commands.command('auto-join-domain')
@CommonOptions.org_option()
@click.option('--domain', required=True, multiple=True)
@click.pass_context
def auto_join_domain(ctx, org, domain):
    data = {}

    add_to_data_if_not_none(data, list(domain), 'domains')

    result = ApiCaller.call(ctx.obj, ctx.obj.session, 'post', 'orgs/{org}/autoJoin'.format(org=org), data)

    output_result(ctx, result, ['ok'])


@orgs_commands.command('remove-members')
@CommonOptions.org_option()
@click.option('--email', required=True, multiple=True)
@click.pass_context
def remove_members_from_org(ctx, org, email):
    data = {'emails': list(email)}

    result = ApiCaller.call(ctx.obj, ctx.obj.session, 'post', 'orgs/{org}/removeMembers'.format(org=org), data)

    for item in result.get('remove_result', []):
        item['removal_result'] = "Removed successfully" if item['removal_result'] else "Failed to find user"

    output_result(ctx, result.get('remove_result', []), ['email', 'removal_result'])


def metadata_params(fn):
    @wraps(fn)
    @click.option('--name', '-n')
    @click.option('--value', '-v')
    @click.option('--add', '-a', is_flag=True)
    @click.option('--replace', '-r', is_flag=True)
    @click.option('--delete', '-d', is_flag=True)
    @click.option('--enable/--disable', default=None)
    @click.pass_context
    def decorated(*args, **kwargs):
        return fn(*args, **kwargs)

    return decorated


@orgs_commands.command('metadata')
@CommonOptions.org_option()
@metadata_params
def add_metadata_org(ctx, org, **kwargs):
    add_metadata(ctx, 'org', org, **kwargs)


def add_metadata(ctx, id_type, id_value, name, value, add, replace, delete, enable):
    data = {}

    if enable is not None:
        value = str(int(enable))

    action, operation = _get_operation_and_action(add, replace, delete, enable, name, value)

    metadata = {
        'operation': operation,
        'name': name,
        'value': value,
    }

    add_to_data_if_not_none(data, metadata, 'metadata')
    add_to_data_if_not_none(data, id_value, id_type)

    result = ApiCaller.call(ctx.obj, ctx.obj.session, action, '{}s/{}/metadata'.format(id_type, id_value), data)

    output_result(ctx, result, ['ok'])


def _get_operation_and_action(add, replace, delete, enable, name, value):
    action = 'post'
    sum_args = int(add + replace + delete + (enable is True) + (enable is False))

    if sum_args > 1:
        raise click.UsageError(
            'Use only --replace/-r or --delete/-d or --add/-a (default value) or --enable or --disable, don\'t use more than one')

    operation = 'DELETE' if delete else 'REPLACE'

    if sum_args == 0:
        if name or value:
            operation = 'ADD'
            add = True
        else:
            action = 'get'
            # TODO: continue with metadata get

    if add:
        operation = 'ADD'

    if not(name and value is not None):
        raise click.UsageError(
            'Use --name/-n and --value/-v to replace/delete/add')

    return action, operation
