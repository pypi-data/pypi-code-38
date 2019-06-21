# -*- coding: utf-8 -*-
import click
from missinglink.commands.commons import add_to_data_if_not_none, output_result, api_get
from missinglink.core.api import ApiCaller

from missinglink.commands.orgs import metadata_params, add_metadata
from missinglink.commands.utilities.options import CommonOptions

UPDATE_SUBSCRIPTION_HEADERS = ['project_name', 'project_id', 'alert_types']


@click.group('projects', help='Project Management Commands.')
def projects_commands():
    pass


@projects_commands.command('list')
@click.pass_context
def list_projects(ctx):
    """Lists the projects that are associated with the current user."""
    projects = api_get(ctx, 'projects')

    output_result(ctx, projects.get('projects', []), ['project_id', 'display_name', 'description', 'token', 'org'])


max_project_display_name = 140
min_project_display_name = 1

max_project_description = 140
min_project_description = 0


@projects_commands.group('alerts')
def alerts_commands():
    """Provides subscribe and unsubscribe facilities for alerts."""
    pass


@alerts_commands.command('subscribe')
@CommonOptions.project_id_option(required=True, multiple=True)
@CommonOptions.alert_type_option(required=True, multiple=True)
@click.pass_context
def subscribe_alert(ctx, project, alert_type):
    """Subscribes the user for alerts in the specified project."""
    data = {
        'alert_types': alert_type,
        'project_ids': project,
    }

    result = ApiCaller.call(ctx.obj, ctx.obj.session, 'post', 'projects/subscribe', data)

    output_result(ctx, result.get('projects', []), UPDATE_SUBSCRIPTION_HEADERS)


@alerts_commands.command('unsubscribe')
@CommonOptions.project_id_option(required=True, multiple=True)
@CommonOptions.alert_type_option(required=True, multiple=True)
@click.pass_context
def unsubscribe_alert(ctx, project, alert_type):
    """Unsubscribes the user for alerts in the specified project."""
    data = {
        'alert_types': alert_type,
        'project_ids': project,
    }

    result = ApiCaller.call(ctx.obj, ctx.obj.session, 'post', 'projects/unsubscribe', data)

    output_result(ctx, result.get('projects', []), UPDATE_SUBSCRIPTION_HEADERS)


@alerts_commands.command('list')
@click.pass_context
def list_alert(ctx):
    """Lists the alerts for which the user is subscribed."""
    alerts = api_get(ctx, 'projects/subscriptions')

    output_result(ctx, alerts.get('alerts', []), ['project_id', 'display_name', 'org', 'alert_type', 'subscribed'])


@projects_commands.command('create')
@CommonOptions.display_name_option(min_length=min_project_display_name, max_length=max_project_display_name)
@CommonOptions.description_option(min_length=min_project_description, max_length=max_project_description)
@CommonOptions.org_option()
# deprecated option but some clients use it
@click.pass_context
def create_project(ctx, display_name, description, org):
    """Creates a project and attaches it to the specified organization."""
    data = {}

    add_to_data_if_not_none(data, display_name, "display_name")
    add_to_data_if_not_none(data, org, "org")
    add_to_data_if_not_none(data, description, "description")

    result = ApiCaller.call(ctx.obj, ctx.obj.session, 'post', 'projects', data)

    output_result(ctx, result, ['id', 'token'])


@projects_commands.command('transfer')
@CommonOptions.project_id_option(required=True)
@click.option('--transfer-to', required=False, help='Organization to transfer to.')
@click.pass_context
def transfer_project(ctx, project, transfer_to):
    """Moves the specified project from one organization to another.

    \b
    To perform this action, both organizations must be accessible to the user."""
    data = {}

    add_to_data_if_not_none(data, transfer_to, "transfer_to")

    result = ApiCaller.call(
        ctx.obj, ctx.obj.session, 'post', 'projects/{project_id}/transfer'.format(project_id=project), data)

    output_result(ctx, result, ['ok'])


@projects_commands.command('metadata')
@CommonOptions.project_id_option(required=True)
@metadata_params
def add_metadata_proj(ctx, project, **kwargs):
    add_metadata(ctx, 'project', project, **kwargs)
