# -*- coding: utf-8 -*-
import click

from missinglink.commands.commons import output_result
from missinglink.commands.utils import monitor_logs
from .utilities.job_parser import JobParser, job_params
from .utilities.options import CommonOptions


@click.group('run', help='runs an experiment on a cluster. By defaults run on a local cluster ')
def run_commands():
    pass


@run_commands.command('track')
@click.pass_context
@CommonOptions.org_option(required=False)
def run_track(ctx, **kwargs):
    jp = JobParser(ctx, **kwargs)
    print(jp.build_src_pointer({}))


def _append_job_data(ctx, org, result, output_keys):
    job_data = result.pop('data', None)

    if not job_data:
        # Until MD-2603 hits production
        return

    result.update(job_data)
    result['name'] = job_data['name']
    result['link'] = "{}/console/{}/queues/{}/jobs/{}".format(
        ctx.obj.config.host,
        org,
        job_data['queue']['id'],
        job_data['id']
    )
    output_keys += ['name', 'link']


@run_commands.command('xp')
@click.pass_context
@job_params
def run_experiment(ctx, **kwargs):
    jp = JobParser(ctx, **kwargs)

    job_env = jp.prepare_job_context()
    if job_env is None:
        # Save recipe
        return

    jp.prepare_encrypted_data(job_env.org, job_env.input_data, job_env.docker_creds, job_env.secure_env)
    result = jp.submit_job(job_env)
    output_keys = ['ok', 'job']

    _append_job_data(ctx, job_env.org, result, output_keys)
    output_result(ctx, result, output_keys)
    _attach(job_env.attach, ctx, job_env.org, result['job'], job_env.disable_colors)


def _attach(attach, ctx, org, job_id, disable_colors):
    if attach:
        url = '{org}/run/{job_id}/logs'.format(org=org, job_id=job_id)
        monitor_logs(ctx, url, disable_colors)


@run_commands.command('logs')
@CommonOptions.org_option()
@click.option('--job', type=str)
@click.option('--disable-colors', is_flag=True, required=False)
@click.option('--lines', '-n', type=click.IntRange(0, 100), required=False)
@click.pass_context
def job_logs(ctx, org, job, disable_colors, lines):
    url = '{org}/run/{job}/logs'.format(org=org, job=job)
    monitor_logs(ctx, url, disable_colors, lines)


def _attach_in_bg(attach, ctx, org, job_id, disable_colors):
    import threading
    thread = threading.Thread(target=_attach, args=(attach, ctx, org, job_id, disable_colors))
    thread.daemon = True
    thread.start()


@run_commands.command('local')
@click.pass_context
@click.option('--link-aws/--no-aws-link', required=False, default=True, help='Allow the job to access you current AWS configuration folder.')
@click.option('--env-aws/--no-aws-env', required=False, default=True, help='Allow the job to access you current AWS environment variables.')
@click.option('--link-gcp/--no-gcp-link', required=False, default=True, help='Allow the job to access you current `gcloud` configuration folder.')
@click.option('--link-azure/--no-azure-link', required=False, default=True, help='Allow the job to access you current Azure configuration folder.')
@click.option('--cache-path', type=str, required=False, help='Path for pip, conda and MissingLink caches')
@job_params
def local(ctx, **kwargs):
    jp = JobParser(ctx, **kwargs)
    jp.validate_no_running_containers()
    jp.docker_tools.pull_rm_image()
    job_env = jp.prepare_job_context()
    if job_env is None:
        # Save recipe
        return

    job_id, docker_command_params = jp.build_local_command(job_env)
    click.echo('Starting Resource Manager for job: %s' % job_id)

    res = jp.run_docker(docker_command_params)
    _attach_in_bg(True, ctx, job_env.org, job_id, job_env.disable_colors)
    for x in res.logs(stream=True, stderr=True, stdout=True):
        click.echo(x.strip())
