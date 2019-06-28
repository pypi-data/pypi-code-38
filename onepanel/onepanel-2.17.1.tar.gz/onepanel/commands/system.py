import os
import sys
import json
import logging
from datetime import timedelta

import click


from onepanel.commands.base import APIViewController
from onepanel.commands.login import login_required
from onepanel.commands.instances import InstanceViewController
from onepanel.commands.jobs import JobViewController

from onepanel.utilities.machine_activity import ThresholdMachineActivity
from onepanel.utilities.machine_activity import MachineActivityMonitor
from onepanel.utilities.machine_activity import MACHINE_ACTIVITY_MONITOR

import onepanel.utilities.s3.wrapper as S3
from onepanel.utilities.s3.authentication import APIProvider

class SystemViewController(APIViewController):
    def __init__(self, conn):
        APIViewController.__init__(self, conn)
        self.instance_view_controller = InstanceViewController(conn)
        self.job_view_controller = JobViewController(conn)

@click.group(help='System command', hidden=True)
@click.pass_context
def system(ctx):
    ctx.obj['vc'] = SystemViewController(ctx.obj['connection'])

@system.command(
    'monitor-activity',
    hidden=True,
    help='''Monitors the machine for activity. Needs 'account_uid/project_uid/workspace_uid' to identify machine. 
            If it is not active after some time, pause request is sent to API.'''
)
@click.argument(
    'identifier',
    type=str,
)
@click.option(
    '-c', '--cpu',
    type=float,
    help='Threshold for CPU. 40 = 40%. Anything below or equal to this is considered an inactive CPU'
)
@click.option(
    '-g', '--gpu',
    type=float,
    help='Threshold for GPU. 40 = 40%. Anything below or equal to this is considered an inactive GPU'
)
@click.option(
    '-d', '--duration',
    type=int,
    help='Duration, in seconds, after which request is sent to API to pause the machine, as it is inactive.'
)
@click.option(
    '-u', '--user-duration',
    type=int,
    help='Duration, in seconds, after which we consider user to be inactive. No commands within this, is inactive.'
)
@click.option(
    '-t', '--time-repeat',
    type=int,
    help='Duration, in seconds, in which the check is performed. E.g. every 5 seconds we check active status'
)
@click.option(
    '-v', '--verbose',
    type=bool,
    is_flag=True,
    default=False,
    help='If true, prints extra messages detailing status'
)
@click.pass_context
def monitor_activity(ctx, identifier, cpu=None, gpu=None, user_duration=None, duration=None, time_repeat=None, verbose=None):
    vc = ctx.obj['vc']

    ids = identifier.split('/')
    account_uid = ids[0]
    project_uid = ids[1]
    instance_uid = ids[2]

    if cpu is None:
        cpu = 40

    if gpu is None:
        gpu = 40

    if duration is None:
        duration = 3600

    if time_repeat is None:
        time_repeat = 60

    if user_duration is None:
        user_duration = 60 * 20  # 20 minutes

    logger = logging.getLogger(MACHINE_ACTIVITY_MONITOR)

    if verbose:
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    def pause_workspace():
        vc.instance_view_controller.pause(account_uid=account_uid, project_uid=project_uid, instance_uid=instance_uid)

    machine_activity = ThresholdMachineActivity(cpu, gpu, timedelta(seconds=user_duration),
                                                dead_duration=timedelta(seconds=duration))

    activity_monitor = MachineActivityMonitor(machine_activity, pause_workspace)
    activity_monitor.delay = time_repeat
    activity_monitor.start()
    activity_monitor.join()


@system.command(
    'print-activity',
    hidden=True,
    help='''Current machine status'''
)
@click.pass_context
def print_activity(ctx):
    machine_activity = ThresholdMachineActivity()
    click.echo(json.dumps(machine_activity.get_statistics(), indent=1))


@system.command('upload-job-code', hidden=True, help='Upload job code')
@click.argument('job_uid', metavar='<job-uid>', type=str)
@click.argument('directory', type=click.Path(), required=False)
@click.option(
    '--project',
    'project_uid',
    type=str,
    required=False,
    help='Project name'
)
@click.option(
    '--account',
    'account_uid',
    type=str,
    required=False,
    help='Account name'
)
@click.pass_context
@login_required
def upload_job_code(ctx, job_uid, directory=None, project_uid=None, account_uid=None):
    vc = ctx.obj['vc']
    vc.job_view_controller.update_config(project_uid, account_uid)

    if directory == None:
        directory = os.getcwd()
    vc.job_view_controller.upload_code(job_uid, directory)

@system.command('download-job-code', hidden=True, help='Download job code')
@click.argument('job_uid', metavar='<job-uid>', type=str)
@click.argument('directory', type=click.Path(), required=False)
@click.option(
    '--project',
    'project_uid',
    type=str,
    required=False,
    help='Project name'
)
@click.option(
    '--account',
    'account_uid',
    type=str,
    required=False,
    help='Account name'
)
@click.pass_context
@login_required
def download_job_code(ctx, job_uid, directory=None, project_uid=None, account_uid=None):
    vc = ctx.obj['vc']
    vc.job_view_controller.update_config(project_uid, account_uid)

    if directory == None:
        directory = os.getcwd()
    vc.job_view_controller.download_code(job_uid, directory)