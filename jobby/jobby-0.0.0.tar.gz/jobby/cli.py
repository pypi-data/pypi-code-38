from __future__ import print_function

import argparse
import os
import shutil
import signal
import subprocess
import sys

from envbash import load_envbash

from jobby.utils import get_env


MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(MODULE_DIR, 'lib')


def _fail(message):
    print('✖︎ ERROR: %s' % message)
    exit(1)


def _checkup_and_load_env():
    work_dir = os.getcwd()
    jobby_dir = os.path.join(work_dir, '.jobby')
    scratch_dir = os.path.join(jobby_dir, 'scratch')
    env_file = os.path.join(jobby_dir, '.env')

    if (not os.path.exists(jobby_dir)) \
            or (not os.path.isdir(jobby_dir)):
        _fail('\'.jobby\' directory not found at \'%s\'.' % work_dir)

    load_envbash(env_file)
    os.environ['JOBBY_LIB_DIR'] = LIB_DIR
    os.environ['JOBBY_WORK_DIR'] = work_dir
    os.environ['JOBBY_SCRATCH_DIR'] = scratch_dir


def init(args):
    work_dir = os.getcwd() \
               if args.path == '.' \
               else os.path.abspath(args.path)
    
    jobby_dir = os.path.join(work_dir, '.jobby')

    if not os.path.exists(work_dir):
        _fail('\'%s\' does not exist.' % work_dir)
    if not os.path.isdir(work_dir):
        _fail('\'%s\' is not a directory.' % work_dir)
    if os.path.exists(jobby_dir):
        _fail('Jobby directory already exists at \'%s\'.' % jobby_dir)
    
    os.makedirs(jobby_dir)
    print('✔ Created Jobby directory: %s' % jobby_dir)

    
    project_name = os.path.basename(work_dir).replace(' ', '_')
    default_environment_variables = [
        ('JOBBY_PROJECT_NAME', project_name),
        ('JOBBY_NETWORK_HOST', '127.0.0.1'),
        ('JOBBY_JOB_CONCURRENCY', '5'),
        ('JOBBY_PYTHON_RUNTIME_ENV', '')]

    final_environment_variables = list()
    for key, default_val in default_environment_variables:
        new_val = raw_input('➜ %s [%s] >>> ' % (key, default_val))

        if key == 'JOBBY_PROJECT_NAME':
            new_val = new_val.replace(' ', '_')

        final_environment_variables.append('%s="%s"\n' % (
            key, new_val if len(new_val) > 0 else default_val))
   
    with open(os.path.join(jobby_dir, '.env'), 'w') as env_file:
        env_file.writelines(final_environment_variables)
    print('✔ Updated Jobby environment file.')

    gitignore_file = os.path.join(work_dir, '.gitignore')
    if os.path.exists(gitignore_file):
        with open(gitignore_file, 'a') as f:
            f.write('\n.jobby/\n')
        print('✔ Added \'.jobby/\' to .gitignore file.')


def start(args):
    _checkup_and_load_env()

    starter_script_path = os.path.join(
        LIB_DIR, 'jobby-start-%s.sh' % args.mode)
    signal.signal(signal.SIGINT, lambda s,f: None)
    subprocess.call(['bash', starter_script_path])


def run(args):
    _checkup_and_load_env()

    runner_script_path = os.path.join(LIB_DIR, 'jobby-run-job.sh')
    signal.signal(signal.SIGINT, lambda s,f: None)
    subprocess.call(['bash', runner_script_path] + args.cmd)


def main():
    parser = argparse.ArgumentParser(prog='jobby')
    subparsers = parser.add_subparsers()
    
    parser_init = subparsers.add_parser(
        'init', help='initialize Jobby settings in a directory')
    parser_init.set_defaults(func=init)
    parser_init.add_argument('-p', '--path', type=str, default='.', 
                             help='directory where Jobby settings are initialized')
    
    parser_start = subparsers.add_parser(
        'start', help='start Jobby in master/worker mode')
    parser_start.set_defaults(func=start)
    parser_start.add_argument('mode', choices=['master', 'worker'], 
                              help='mode in which Jobby should be started')

    parser_run = subparsers.add_parser(
        'run', help='run python script on a Jobby worker')
    parser_run.set_defaults(func=run)
    parser_run.add_argument('cmd', nargs=argparse.REMAINDER,
                            help='python script with arguments that is to be run')

    args = parser.parse_args()
    args.func(args)
