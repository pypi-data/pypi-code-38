from pathlib import Path

import gitlab as glapi

from devo.config import read_config, read_yaml, persist_yaml

GITLAB_CONFIG = '.devo/gitlab.yaml'
CI_CREDENTIALS_FILE = '.devo/credentials.env'
CI_CREDENTIALS_VARIABLE = 'DEVO_CREDENTIALS'

K8S_PROD_ENV_FILE = 'k8s/prod/prod.env'
K8S_PROD_ENV_VARIABLE = 'DEVO_K8S_PROD_ENV'


def read_env_file(env):
    return open(env, 'r').read()


def persist_env_file(env, data):
    with open(env, 'w') as f:
        f.write(data)


def read_gitlab_config():
    current_path = Path.cwd() / GITLAB_CONFIG
    return read_yaml(current_path)


def persist_gitlab_config(data):
    current_path = Path.cwd() / GITLAB_CONFIG
    persist_yaml(current_path, data)


def gitlab_file_exists():
    return (Path.cwd() / GITLAB_CONFIG).exists()


def get_gitlab_api():
    config = read_config()
    gitlab_config = read_gitlab_config()
    gl = glapi.Gitlab(config['gitlab']['url'], gitlab_config['gitlab_token'])
    return gl


def get_gitlab_project():
    gl = get_gitlab_api()
    config = read_config()
    project = gl.projects.get(config['gitlab']['project_id'])
    return project


def push_env_file_as_variable(variable, file):
    payload = {'key': variable, 'value': read_env_file(file), 'variable_type': 'file'}
    project = get_gitlab_project()
    try:
        project.variables.get(variable)
        project.variables.update(id=variable, new_data=payload)
    except glapi.GitlabGetError as e:
        if e.response_code == 404:
            project.variables.create(payload)
            return


def pull_variable_as_env_file(variable, file):
    try:
        project = get_gitlab_project()
        var = project.variables.get(variable)
        persist_env_file(file, var.value)
    except glapi.GitlabGetError as e:
        if e.response_code == 404:
            return


def push_credentials_env():
    push_env_file_as_variable(CI_CREDENTIALS_VARIABLE, CI_CREDENTIALS_FILE)


def pull_credentials_env():
    pull_variable_as_env_file(CI_CREDENTIALS_VARIABLE, CI_CREDENTIALS_FILE)


def push_k8s_prod_env():
    push_env_file_as_variable(K8S_PROD_ENV_VARIABLE, K8S_PROD_ENV_FILE)


def pull_k8s_prod_env():
    pull_variable_as_env_file(K8S_PROD_ENV_VARIABLE, K8S_PROD_ENV_FILE)
