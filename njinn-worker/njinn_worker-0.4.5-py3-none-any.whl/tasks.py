import configparser
import json
import os
import shutil
import subprocess
import sys
import traceback
import uuid
from contextlib import contextmanager
from pathlib import Path

import git
import requests
import virtualenv
from celery.utils.log import get_task_logger

from api_client import NjinnAPI
from worker.__main__ import get_celery_app

app = get_celery_app()
log = get_task_logger(__name__)


def get_config_path():
    working_dir = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(working_dir, 'njinn.ini')
    return config_path


def get_njinn_api():
    """
    Set the NjinnAPI class to make authenticated calls.
    """

    config = configparser.ConfigParser()
    config.read(get_config_path())

    api = config['DEFAULT']['njinn_api']
    secret = config['DEFAULT']['secret']
    worker_name = config['DEFAULT']['name']
    execution_id = context['njinn_execution_id']

    njinn_api = NjinnAPI(api, secret, worker_name, execution_id)
    return njinn_api


def get_pack(pack_path):
    pack_api = '/api/v1/workercom/' + pack_path

    response = njinn_api.get(pack_api)

    if response.status_code != requests.codes.ok:
        raise Exception(
            f"Problem trying to get {pack_api}. API responded with ({response.status_code}): {response.text}")

    return response.json()


def clone_repository(repository_path, pack_path):
    """
    Clone repository from pack repository url to the 'repository_path' path.
    """

    pack = get_pack(pack_path)

    repository_url = pack['repository']
    branch = pack['branch']
    pack_namespace = pack['namespace']
    pack_name = pack['name']

    git.Repo.clone_from(repository_url, repository_path, branch=branch)

    venv_path = f'./venv/{pack_namespace}/{pack_name}'
    virtualenv.create_environment(venv_path, clear=True)

    install_requests_jwt_and_cryptography(pack)
    install_requirements(pack, pack_path)


def update_repository(repository_path, pack_path):
    """
    Update the repository at 'repository_path' from remote pack repository.
    """

    pack = get_pack(pack_path)
    pack_branch = pack['branch']

    repo = git.Repo(repository_path)

    if repo.active_branch is not pack_branch:
        repo.git.checkout(pack_branch)

    origin = repo.remotes.origin
    origin.fetch()

    commits_behind = list(repo.iter_commits(
        f'{pack_branch}..origin/{pack_branch}'))
    commits_ahead = list(repo.iter_commits(
        f'origin/{pack_branch}..{pack_branch}'))

    if repo.is_dirty() or commits_behind or commits_ahead:
        repo.git.reset('--hard', f'origin/{pack_branch}')

        install_requirements(pack, pack_path)


def install_requests_jwt_and_cryptography(pack):
    """
    Install ``requests_jwt`` and ``cryptography`` packages.
    """

    pack_namespace = pack['namespace']
    pack_name = pack['name']

    venv_path = f'./venv/{pack_namespace}/{pack_name}'
    dir_path = os.path.dirname(os.path.realpath(__file__))

    subprocess.check_call(
        [f"{venv_path}/bin/pip", 'install', 'requests_jwt', 'cryptography'],
        universal_newlines=True,
        cwd=dir_path
    )


def install_requirements(pack, pack_path):
    """
    Install requirements if 'requirements.txt' file is provided. 
    """

    pack_namespace = pack['namespace']
    pack_name = pack['name']

    venv_path = f'./venv/{pack_namespace}/{pack_name}'
    requirements_path = f"./{pack_path}/requirements.txt"
    dir_path = os.path.dirname(os.path.realpath(__file__))

    if os.path.exists(requirements_path):
        subprocess.check_call(
            [f"{venv_path}/bin/pip", 'install', '-r', requirements_path],
            universal_newlines=True,
            cwd=dir_path
        )


@contextmanager
def virtualenv_context(virtualenv_dir):
    """
    A context manager for executing commands within the context of a
    Python virtualenv.
    """

    old_path = os.environ['PATH']
    virtualenv_bin_dir = (Path(virtualenv_dir) / 'bin').resolve()
    new_path = '{}:{}'.format(str(virtualenv_bin_dir), old_path)
    os.environ['PATH'] = new_path
    try:
        yield
    finally:
        os.environ['PATH'] = old_path


def report_action_result(action_output):
    """
    Report action result of the task to the Njinn API.
    """

    action_output['context'] = context
    log.info(f"Action Output: {action_output}")

    result_api = '/api/v1/workercom/results'
    log.info(f"Calling {result_api}")

    r = njinn_api.post(result_api, json=action_output)
    log.info(f"Response: {r.status_code}")


@app.task(name='njinn_execute')
def njinn_execute(action, pack, action_context):
    global context

    try:
        context = dict()
        context['action_execution_id'] = action_context.get(
            'action_execution_id')
        context['task_name'] = action_context.get('task_name')
        context['execution_id'] = action_context.get('execution_id')
        context['njinn_execution_id'] = action_context.get(
            'njinn_execution_id')

        global njinn_api
        njinn_api = get_njinn_api()

        abspath = os.path.abspath(__file__)
        dname = os.path.dirname(abspath)
        os.chdir(dname)

        dir_path = os.path.dirname(os.path.realpath(__file__))

        log.info("Njinn task initiating")

        pack_namespace, pack_name = pack.split('.')
        pack_path = f"packs/{pack_namespace}/{pack_name}"
        pack_full_path = os.path.join(dir_path, pack_path)

        if not os.path.isdir(pack_full_path):
            clone_repository(pack_full_path, pack_path)
        else:
            update_repository(pack_full_path, pack_path)

        action_execution_id = action_context.get('action_execution_id')
        working_dir = os.path.join('working', action_execution_id)
        os.makedirs(working_dir)

        input_file = os.path.join(working_dir, 'in.json')
        input_file_content = {
            'config_path': get_config_path(),
            'action': action,
            'pack': pack,
            'action_context': action_context
        }

        with open(input_file, 'w') as fp:
            json.dump(input_file_content, fp)

        cmd = f'python action.py {input_file}'

        log.info('Running: %s', cmd)

        venv_path = f'./venv/{pack_namespace}/{pack_name}'
        with virtualenv_context(venv_path):
            proc = subprocess.check_call(
                cmd,
                universal_newlines=True,
                cwd=dir_path,
                shell=True
            )

        with open(os.path.join(working_dir, 'out.json')) as output_file:
            action_output = json.load(output_file)

        report_action_result(action_output)

        shutil.rmtree(working_dir)

    except Exception as e:
        error = traceback.format_exc()
        log.error(error)
        result = {"state": "ERROR", "output": {"error": error}, "log": error}
        report_action_result(result)

    return None
