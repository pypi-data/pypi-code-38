from __future__ import (absolute_import, division, print_function, unicode_literals)

import codecs
import os
import subprocess
import time

import click

from .klass_counter import Counter
from .klass_data import Data
from .klass_path import Path
from .klass_print import Print
from .klass_str import Str
from .klass_yaml_config import YamlConfig

JOB_PATH = os.path.join(Path.home(), '.dyvz', 'jobs.yml')


@click.group()
@click.pass_context
def cli_job(ctx):
    yaml = YamlConfig(JOB_PATH, create_if_not_exists=True)
    ctx.obj = {}
    ctx.obj['yaml'] = yaml


@cli_job.command('create')
@click.argument('name', type=click.STRING, required=True)
@click.argument('data', type=click.STRING, required=True)
@click.option('--description', type=click.STRING, required=False, help='A description of the job', )
@click.pass_context
def __create(ctx, name, data, description):
    """Create a job"""
    yaml = ctx.obj['yaml']
    if yaml.get(name=name):
        Print.error('the job [%s] already exists' % name)
    commands = [data]
    if os.path.isfile(data):
        commands = open(data).read().split('\n')
    yaml.add(name, description=description or '', commands=commands)
    yaml.dump()
    Print.success('The job [%s] is successfully added' % name)


@cli_job.command('update')
@click.argument('name', type=click.STRING, required=True)
@click.argument('data', type=click.STRING, required=True)
@click.option('--description', type=click.STRING, required=False, help='A description of the job', )
@click.pass_context
def __update(ctx, name, data, description):
    """Update a job"""
    yaml = ctx.obj['yaml']
    if not yaml.get(name=name):
        Print.error('the job [%s] is not exists' % name)
    commands = [data]
    if os.path.isfile(data):
        commands = open(data).read().split('\n')
    yaml.add(name, description=description or name, commands=commands)
    yaml.dump()
    Print.success('The job [%s] is successfully updated' % name)


@cli_job.command('delete')
@click.argument('name', type=click.STRING, required=True)
@click.pass_context
def __delete(ctx, name):
    """Delete a job"""
    yaml = ctx.obj['yaml']
    if not yaml.get(name=name):
        Print.error('the job [%s] is not exists' % name)
    if click.confirm('Are you sure, you want to delete [%s] ?' % name):
        yaml.delete(name=name)
        yaml.dump()
        Print.success('The job [%s] is deleted' % name)
    else:
        Print.warning('Aborted')


@cli_job.command('list')
@click.argument('grep', type=click.STRING, required=False)
@click.pass_context
def __list(ctx, grep):
    """List all jobs"""
    yaml = ctx.obj['yaml']
    Data(yaml.get_list(), header=['name', 'description']).show(grep=grep)


def __execute_commands(description, confirm, commands, prefix, suffix):
    last_command = False
    for command in commands:
        rerun = False
        if not command.strip():
            continue
        if (Str(command).is_equal('#confirm') or Str(command).is_equal('#continue')) and not confirm:
            if not click.confirm('Continue ?'):
                Print.abort()
            continue
        if Str(command).is_equal('#clear'):
            click.clear()
            continue
        if Str(command).is_equal('#break'):
            break
        if Str(command).is_equal('#rerun'):
            rerun = True
            command = last_command
        if not command or command.strip()[0].lower() in ['#', ';']:
            continue
        if description != command:
            Print.info(description)
        if not rerun:
            if prefix:
                command = prefix + ' ' + command
            if suffix:
                command = command + ' ' + suffix
        while True:
            if confirm:
                if not click.confirm('Execute the command : [%s] ?' % command):
                    Print.abort()
            else:
                Print.info('Command : [%s]' % command)
            p = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            out, err = p.communicate()
            if err:
                Print.error(err)
            if out:
                Print.info(out)
            if rerun:
                if click.confirm('Rerun the command : [%s] ?' % command):
                    continue
            break
        last_command = command


@cli_job.command('run')
@click.argument('name', type=click.STRING, required=True, )
@click.option('--number', '-n', type=click.INT, default=1, required=False,
              help='How many times the job should be executed, -1 to infinite execution', )
@click.option('--sleep', '-s', type=click.INT, default=0, required=False,
              help='Case times up to 1, the time to sleep before to resume the execution (in seconds)', )
@click.option('--prompt', is_flag=True, default=False, help='Case times up to 1, prompt before resume the execution')
@click.option('--confirm', is_flag=True, default=False,
              help='Case of a file of many commands, prompt before execution of a command')
@click.option('--clear', is_flag=True, default=False, help='Case times up to 1, clear the console before to resume', )
@click.option('--time', 'time_', is_flag=True, default=False, help='Show the execution time', )
@click.option('--inline', is_flag=True, default=False,
              help='Force that the first argument given to job is a command and a file nor a job name', )
@click.option('--prefix', type=click.STRING, default='', required=False, help='Add a prefix to the command', )
@click.option('--suffix', type=click.STRING, default='', required=False, help='Add a suffix to the command', )
@click.pass_context
def __run(ctx, name, number, sleep, prompt, confirm, clear, time_, inline, prefix, suffix):
    """Run a job
    The first argument can be :
        - Name of a job
        - command if --inline provided
        - path of a file of commands
    """
    counter = Counter('global')
    counter.start()
    yaml = ctx.obj['yaml']
    commands = []
    description = name
    if os.path.isfile(name):
        with codecs.open(name, encoding='utf8', mode='r') as job_file:
            for line in job_file.readlines():
                line = line.strip()
                if not line:
                    continue
                commands.append(line)
    elif inline:
        commands.append(name)
    else:
        data = yaml.get_values(_name=name)
        if not data:
            Print.error('the job [%s] is not exists' % name)
        commands = data.get('commands', [])
        description = data.get('description', name)
    index = 0
    while number != 0:
        index += 1
        if clear:
            click.clear()
        Print.info('')
        __execute_commands(description, confirm, commands, prefix, suffix)
        if time_:
            counter.print(title='elapsed time')
        number -= 1
        if number != 0:
            time.sleep(sleep)
            if prompt:
                if click.confirm('Continue ?'):
                    continue
                else:
                    break
