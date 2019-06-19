import contextlib
import os
import shutil
import subprocess
import sys
import tempfile
import time
import json

import click
import dong
from dong import auth
from dong import net
from dong import utils
from dong.decorators import login_required
import dong.httpclient as httpclient


def is_training_succeeded(job):
    r = httpclient.get('api/v1/train/{}/'.format(job))
    result = r.json()
    if result['status'] == 'Succeeded':
        return True
    else:
        return False


def _wait_for_completion(job):
    count = 0
    while is_training_succeeded(job) is False:
        print('.', end='', flush=True)
        time.sleep(1)
        count += 1

    print('👍')


@contextlib.contextmanager
def _tempdir(change_to=False):
    temp_dir = tempfile.mkdtemp()
    cur_dir = None
    if change_to:
        cur_dir = os.getcwd()
        os.chdir(temp_dir)

    yield temp_dir

    if cur_dir is not None:
        os.chdir(cur_dir)

    _rmtree(temp_dir)


def _copytree(source_dir, temp_dir):
    dest_dir = os.path.join(temp_dir, 'dest')
    shutil.copytree(source_dir, dest_dir)
    return dest_dir


def _rmtree(path):
    shutil.rmtree(path)


def _exec(setup_py_path, setup_py_args, env=None):
    args = ['python', setup_py_path] + setup_py_args
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    (stdout, stderr) = p.communicate()

    return p.returncode


@contextlib.contextmanager
def _cd(working_dir):
    curdir = os.getcwd()
    try:
        os.chdir(working_dir)
        yield
    finally:
        os.chdir(curdir)


def _run_setuptools(package_root, setup_py_path, output_dir):
    with _cd(package_root):
        sdist_args = ['sdist', '--dist-dir', output_dir]
        setup_py_args = sdist_args

        _exec(setup_py_path, setup_py_args)

        local_paths = [os.path.join(output_dir, rel_file)
                       for rel_file in os.listdir(output_dir)]
        return local_paths


def _upload_package(password, module_name, path_to_file, message, args):
    file_name = os.path.basename(path_to_file)

    multipart_form_data = {
        'file': (file_name, open(path_to_file, 'rb')),
        'module_name': (None, module_name),
        'message': (None, message),
        'args': (None, args)
    }
    headers = net.authorization_headers(password)
    r = httpclient.post('api/v1/train/', files=multipart_form_data, headers=headers)
    result = r.json()

    if 'name' in result:
        return r.json()['name']
    else:
        return None


def _build_packages(package_path, output_dir):
    package_path = os.path.abspath(package_path)
    package_root = os.path.dirname(package_path)

    with _tempdir(True) as working_dir:
        package_root = _copytree(package_root, working_dir)

        setup_py_path = os.path.join(package_root, 'setup.py')
        return _run_setuptools(package_root, setup_py_path, output_dir)


def _execute(password, package_path, module_name, message, args):
    with _tempdir(False) as working_dir:
        print("Building package...")
        paths = _build_packages(package_path,
                                os.path.join(working_dir, 'output'))
        path_to_file = paths[0]
        print("Uploading package...")
        try:
            job_name = _upload_package(password, module_name, path_to_file, message, args)
        except Exception as e:
            job_name = None

        if job_name is None:
            print("Can't upload package, stopped.")
            return

        print('Job name: {}'.format(job_name))


@click.group()
def command():
    """Training job."""
    pass


@command.command()
@click.option('--package-path', default=None)
@click.option('-m', '--message', prompt='Training message')
@click.argument('args', nargs=-1)
@click.pass_context
def exec(ctx, package_path, message,args):
    """Execute training job."""

    module_name = utils.get_project_name('./setup.py' if package_path is None else os.path.join(os.path.dirname(package_path),
                                                                                                'setup.py'))
    if module_name == '' or len(module_name.split('/')) > 1:
        click.secho('setup.py not found under ' + ('current working directory' if package_path is None else os.path.dirname(package_path)),
                    fg='red',
                    err=True)
        ctx.exit(1)
        return

    if package_path is None:
        package_path = './' + module_name        
    
    print('Use dong ML project: ' + module_name)
    print('Project path: ' + os.path.abspath(os.path.dirname(package_path)))

    (login, password) = auth.get_credential_or_exit()
    _execute(password, package_path, module_name, message, json.dumps(list(args)))


@command.command()
@click.option('-j', '--job-name', required = True)
def status(job_name):
    """Retrieve training status, training message note."""

    (login, password) = auth.get_credential_or_exit()
    headers = net.authorization_headers(password)
    try:
        r = httpclient.get('api/v1/train/{}/'.format(job_name), headers=headers)
        result = r.json()
        output = """name: {}
message: {}
status: {}""".format(result['job_name'], result['message'], result['status'])
    except Exception as e:
        output = "Can't get any status of training job: {}, stopped.".format(job_name)

    print(output)


@command.command()
@click.option('-j', '--job-name')
def kill(job_name):
    """kill running job."""

    (login, password) = auth.get_credential_or_exit()
    headers = net.authorization_headers(password)
    try:
        r = httpclient.post('api/v1/train/{}/kill'.format(job_name), headers=headers)
        result = r.json()
        output=""
#        output = """name: {}
#status: {}""".format(result['name'], result['status'])
    except Exception as e:
        output = "fail to kill {}".format(job_name)
    print(output)
