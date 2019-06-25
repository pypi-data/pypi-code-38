# -*- coding: utf-8 -*-
import logging
from functools import wraps
import botocore
import click
from click import exceptions

from missinglink.commands.utilities.options import CommonOptions
from .cloud.aws import AwsContext
from missinglink.core.context import Expando
from .resources import resources_commands


@resources_commands.group('aws')
@click.option('--region', envvar="ML_AWS_REGION", help='AWS region to use', default='us-east-2', required=False)
@click.pass_context
def aws_commands(ctx, **kwargs):
    ctx.obj.aws = Expando()
    ctx.obj.aws.region = kwargs.pop('region', None)


def handle_aws_errors(fn):
    @wraps(fn)
    def try_call(*args, **kwargs):
        # noinspection PyUnresolvedReferences
        try:
            return fn(*args, **kwargs)
        except botocore.exceptions.NoCredentialsError as ex:
            logging.info('Failed to validate authentication', exc_info=1)
            raise exceptions.ClickException('AWS configuration is incomplete. Please run `aws configure`. Error: %s' % str(ex))

    return try_call


@aws_commands.command('init', help='Initialize Resource Management on AWS, creating the cloud connection and the default queue and resource group.')
@CommonOptions.org_option()
@click.option('--ssh-key-path', default=None, help='SSH Key to use for git clone commands, and for connecting to virtual machines')
@click.option('--region', envvar="ML_AWS_REGION", help='AWS region to use', required=False)
@click.option('--queue', required=False)
@handle_aws_errors
@click.pass_context
def init_auth(ctx, **kwargs):
    ctx.obj.aws.region = kwargs.pop('region', None) or ctx.obj.aws.region
    aws = AwsContext(ctx, kwargs)
    queue = aws.kwargs.get('queue')

    if queue:
        # This will fail when the group is not present
        aws.get_queue(queue)

    aws.encrypt_and_send_connector()
    aws.setup_spot_role_if_needed()
    aws.setup_vpc_if_needed()
    aws.setup_s3_if_needed()
    click.echo(aws.auth_state)
