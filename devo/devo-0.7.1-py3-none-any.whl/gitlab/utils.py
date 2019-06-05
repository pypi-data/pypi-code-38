import gitlab as glapi

from devo.config import read_config, read_creds


def replace_variable(project, key, value):
    try:
        var = project.variables.get(key)
    except glapi.GitlabError as e:
        if e.response_code == 404:
            project.variables.create({'key': key, 'value': value})
            return
        else:
            raise e
    var.delete()
    project.variables.create({'key': key, 'value': value})


def sync_variables_to_gitlab():
    config = read_config()
    creds = read_creds()
    gl = glapi.Gitlab(config['gitlab']['url'], creds['gitlab_token'])

    project = gl.projects.get(config['gitlab']['project_id'])

    if not creds['ci_registry_user'].startswith('$'):
        replace_variable(project, 'CI_REGISTRY_USER', creds['ci_registry_user'])
    if not creds['ci_registry_password'].startswith('$'):
        replace_variable(project, 'CI_REGISTRY_PASSWORD', creds['ci_registry_password'])
    if config['registry']['url']:
        replace_variable(project, 'CI_REGISTRY', config['registry']['url'])

    replace_variable(project, 'KUBE_URL', creds['kube_url'])
    replace_variable(project, 'KUBE_USER', creds['kube_user'])
    replace_variable(project, 'KUBE_TOKEN', creds['kube_token'])
