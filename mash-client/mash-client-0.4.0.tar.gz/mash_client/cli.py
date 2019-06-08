# -*- coding: utf-8 -*-

"""mash client CLI endpoints using click library."""

# Copyright (c) 2018 SUSE LLC
#
# This file is part of mash_client. mash_client provides a command line
# utility for interfacing with a MASH server.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import click
import json
import logging

from mash_client.cli_utils import (
    EC2_PARTITIONS,
    get_config,
    handle_errors,
    handle_request,
    SUPPORTED_CLOUDS
)


def print_license(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('GPLv3+')
    ctx.exit()


def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()


@click.group()
@click.version_option()
@click.option(
    '--license',
    is_flag=True,
    callback=print_license,
    expose_value=False,
    is_eager=True,
    help='Show license information.'
)
@click.option(
    '-C',
    '--config',
    type=click.Path(exists=True),
    help='MASH client config file to use. Default: '
         '~/.config/mash_client/config'
)
@click.option(
    '--no-color',
    is_flag=True,
    help='Remove ANSI color and styling from output.'
)
@click.option(
    '--host',
    help='Resolvable hostname for the MASH server instance.'
)
@click.option(
    '--port',
    help='The port number the MASH server is listening on.'
)
@click.option(
    '--debug',
    'log_level',
    flag_value=logging.DEBUG,
    help='Display debug level logging to console.'
)
@click.option(
    '--verbose',
    'log_level',
    flag_value=logging.INFO,
    default=True,
    help='Display logging info to console. (Default)'
)
@click.option(
    '--quiet',
    'log_level',
    flag_value=logging.WARNING,
    help='Disable console output.'
)
@click.pass_context
def main(context, config, no_color, host, port, log_level):
    """
    The command line interface allows you to interact with a MASH server.

    It provides commands to submit jobs to the MASH server pipeline or
    add/delete a user account.
    """
    if context.obj is None:
        context.obj = {}

    context.obj['config'] = config
    context.obj['no_color'] = no_color
    context.obj['host'] = host
    context.obj['port'] = port
    context.obj['log_level'] = log_level


@click.group()
def job():
    """
    Submit job requests, addition or deletion, to the MASH server pipeline.
    """


@click.command()
@click.argument(
    'document',
    type=click.Path(exists=True)
)
@click.pass_context
def add(context, document):
    """
    Send add job request to mash server based on provided json document.
    """
    config_data = get_config(context.obj)

    with handle_errors(config_data['log_level'], config_data['no_color']):
        with open(document) as job_file:
            job_data = json.load(job_file)

        handle_request(config_data, '/add_job', job_data)


@click.command()
@click.option(
    '--force',
    is_flag=True,
    callback=abort_if_false,
    expose_value=False,
    help='Force deletion without prompt.',
    prompt='Are you sure you want to delete job?'
)
@click.option(
    '--job-id',
    type=click.UUID,
    required=True,
    help='The UUID of the job to be removed '
         'from the MASH server pipeline.'
)
@click.pass_context
def delete(context, job_id):
    """
    Delete the job with the given ID from the MASH server pipeline.
    """
    config_data = get_config(context.obj)

    with handle_errors(config_data['log_level'], config_data['no_color']):
        handle_request(config_data, '/delete_job/{0}'.format(job_id))


@click.group()
def account():
    """
    Submit account requests to the MASH server.
    """


@click.command(
    name='delete', context_settings=dict(token_normalize_func=str.lower)
)
@click.option(
    '--force',
    is_flag=True,
    callback=abort_if_false,
    expose_value=False,
    help='Force deletion without prompt.',
    prompt='Are you sure you want to delete account?'
)
@click.option(
    '--name',
    type=click.STRING,
    required=True,
    help='Name of the account to be deleted.'
)
@click.option(
    '--cloud',
    type=click.Choice(SUPPORTED_CLOUDS),
    required=True,
    help='The target cloud framework for this job.'
)
@click.option(
    '--mash-user',
    type=click.STRING,
    required=True,
    help='The user in MASH user space to delete the account from.'
)
@click.pass_context
def delete_account(context, name, cloud, mash_user):
    """
    Delete an account in the user name space on the MASH server.
    """
    config_data = get_config(context.obj)

    with handle_errors(config_data['log_level'], config_data['no_color']):
        job_data = {
            'account_name': name,
            'cloud': cloud,
            'requesting_user': mash_user
        }
        handle_request(config_data, '/delete_account', job_data)


@click.group(name='add')
def add_account():
    """
    Handle mash account add requests.
    """


@click.command(
    name='ec2', context_settings=dict(token_normalize_func=str.lower)
)
@click.option(
    '--additional-regions',
    is_flag=True,
    help='Invoke region addition process to specify information '
         'for additional regions'
)
@click.option(
    '--group',
    type=click.STRING,
    help='Group name to associate the account with.'
)
@click.option(
    '--name',
    type=click.STRING,
    required=True,
    help='Name for the account to create.'
)
@click.option(
    '--partition',
    type=click.Choice(EC2_PARTITIONS),
    required=True,
    help='The location of the EC2 account. ["aws", "aws-cn", "aws-us-gov"]'
)
@click.option(
    '--mash-user',
    type=click.STRING,
    required=True,
    help='The user in MASH user space to add the account for.'
)
@click.option(
    '--region',
    type=click.STRING,
    required=True,
    help='The target region for image upload and testing.'
)
@click.option(
    '--access-key-id',
    type=click.STRING,
    required=True,
    help='AWS access key.'
)
@click.option(
    '--secret-access-key',
    type=click.STRING,
    required=True,
    help='AWS secret access key.'
)
@click.pass_context
def add_ec2_account(
    context, additional_regions, group, name, partition,
    mash_user, region, access_key_id, secret_access_key
):
    """
    Add an EC2 account in the user name space on the MASH server.
    """
    config_data = get_config(context.obj)

    with handle_errors(config_data['log_level'], config_data['no_color']):
        data = {
            'account_name': name,
            'credentials': {
                'access_key_id': access_key_id,
                'secret_access_key': secret_access_key
            },
            'partition': partition,
            'cloud': 'ec2',
            'requesting_user': mash_user,
            'region': region
        }

        if additional_regions:
            regions = []

            while True:
                if click.confirm('Add an additional region?'):
                    name = click.prompt('Enter the region name', type=str)
                    helper_image = click.prompt(
                        'Enter the helper image id',
                        type=str
                    )

                    regions.append({
                        'name': name,
                        'helper_image': helper_image
                    })
                else:
                    break

            data['additional_regions'] = regions

        if group:
            data['group'] = group

        handle_request(config_data, '/add_account', data)


@click.command(
    name='azure', context_settings=dict(token_normalize_func=str.lower)
)
@click.option(
    '--group',
    type=click.STRING,
    help='Group name to associate the account with.'
)
@click.option(
    '--name',
    type=click.STRING,
    required=True,
    help='Name for the account to create.'
)
@click.option(
    '--region',
    type=click.STRING,
    required=True,
    help='The region where the test instance will be launched.'
)
@click.option(
    '--mash-user',
    type=click.STRING,
    required=True,
    help='The user in MASH user space to add the account for.'
)
@click.option(
    '--source-container',
    type=click.STRING,
    required=True,
    help='The name of the container that images will be'
         ' uploaded to and tested.'
)
@click.option(
    '--source-resource-group',
    type=click.STRING,
    required=True,
    help='The name of the resource group where '
         'the source storage account exists.'
)
@click.option(
    '--source-storage-account',
    type=click.STRING,
    required=True,
    help='The name of the ARM based storage account '
         'where the source container exists.'
)
@click.option(
    '--destination-container',
    type=click.STRING,
    required=True,
    help='The name of the container that images will be'
         ' copied to and published from.'
)
@click.option(
    '--destination-resource-group',
    type=click.STRING,
    required=True,
    help='The name of the resource group where '
         'the destination storage account exists.'
)
@click.option(
    '--destination-storage-account',
    type=click.STRING,
    required=True,
    help='The name of the ASM based storage account where '
         'the destination container exists.'
)
@click.option(
    '--credentials',
    type=click.Path(exists=True),
    required=True,
    help='The JSON service account credentials file.'
)
@click.pass_context
def add_azure_account(
    context, group, name, region, mash_user, source_container,
    source_resource_group, source_storage_account,
    destination_container, destination_resource_group,
    destination_storage_account, credentials
):
    """
    Add an Azure account in the user name space on the MASH server.
    """
    config_data = get_config(context.obj)

    with handle_errors(config_data['log_level'], config_data['no_color']):
        with open(credentials) as credentials_file:
            creds = json.load(credentials_file)

        data = {
            'account_name': name,
            'credentials': creds,
            'cloud': 'azure',
            'region': region,
            'requesting_user': mash_user,
            'source_container': source_container,
            'source_resource_group': source_resource_group,
            'source_storage_account': source_storage_account,
            'destination_container': destination_container,
            'destination_resource_group': destination_resource_group,
            'destination_storage_account': destination_storage_account
        }

        if group:
            data['group'] = group

        handle_request(config_data, '/add_account', data)


@click.command(
    name='gce', context_settings=dict(token_normalize_func=str.lower)
)
@click.option(
    '--group',
    type=click.STRING,
    help='Group name to associate account with.'
)
@click.option(
    '--name',
    type=click.STRING,
    required=True,
    help='Name for the account to add.'
)
@click.option(
    '--bucket',
    type=click.STRING,
    required=True,
    help='The storage bucket where images will be uploaded.'
)
@click.option(
    '--zone',
    type=click.STRING,
    required=True,
    help='The zone where the test instances will be launched.'
)
@click.option(
    '--mash-user',
    type=click.STRING,
    required=True,
    help='The user in MASH user space to add the account for.'
)
@click.option(
    '--testing-account',
    type=click.STRING,
    help='The name of the testing account that '
         'will be used for launching test instances.'
)
@click.option(
    '--is-publishing-account',
    is_flag=True,
    help='The new account is a publishing account.'
)
@click.option(
    '--credentials',
    type=click.Path(exists=True),
    required=True,
    help='The JSON service account credentials file.'
)
@click.pass_context
def add_gce_account(
    context, group, name, bucket, zone, mash_user, testing_account,
    is_publishing_account, credentials
):
    """
    Add a GCE account in the user name space on the MASH server.
    """
    config_data = get_config(context.obj)

    with handle_errors(config_data['log_level'], config_data['no_color']):
        with open(credentials) as credentials_file:
            creds = json.load(credentials_file)

        data = {
            'account_name': name,
            'bucket': bucket,
            'credentials': creds,
            'cloud': 'gce',
            'region': zone,
            'requesting_user': mash_user
        }

        if group:
            data['group'] = group

        if testing_account:
            data['testing_account'] = testing_account

        if is_publishing_account:
            data['is_publishing_account'] = True

        handle_request(config_data, '/add_account', data)


job.add_command(add)
job.add_command(delete)
main.add_command(job)
account.add_command(delete_account)
add_account.add_command(add_ec2_account)
add_account.add_command(add_azure_account)
add_account.add_command(add_gce_account)
account.add_command(add_account)
main.add_command(account)
