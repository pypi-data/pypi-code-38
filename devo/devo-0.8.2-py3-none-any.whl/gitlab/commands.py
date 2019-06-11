import click

from .utils import push_credentials_env, pull_credentials_env, \
    push_k8s_prod_env, pull_k8s_prod_env, gitlab_file_exists, persist_gitlab_config


@click.group()
def gitlab():
    pass


@gitlab.group()
def push():
    pass


@gitlab.group()
def pull():
    pass


def check_gitlab_file():
    if not gitlab_file_exists():
        raise click.Abort('No gitlab.yaml configuration found. Please run ``devo gitlab init`` first.')


@push.command(name='creds')
def creds_push():
    """Push the .devo/credentials.env to the Gitlab project as a CI variable called DEVO_CREDENTIALS"""
    check_gitlab_file()
    push_credentials_env()
    click.echo('Credentials have been pushed to Gitlab as CI variable')


@pull.command(name='creds')
def creds_pull():
    """Pull the contents of the Gitlab CI variable DEVO_CREDENTIALS into .devo/credentials.env"""
    check_gitlab_file()
    pull_credentials_env()
    click.echo('Credentials have been pulled from Gitlab CI variable')


@push.command(name='k8s')
def k8s_push():
    """Push the k8s/prod/prod.env to the Gitlab project as a CI variable called DEVO_K8S_PROD_ENV"""
    check_gitlab_file()
    push_k8s_prod_env()
    click.echo('k8s production secrets have been pushed to Gitlab as CI variable')


@pull.command(name='k8s')
def k8s_pull():
    """Pull the contents of the Gitlab CI variable DEVO_K8S_PROD_ENV into k8s/prod/prod.env"""
    check_gitlab_file()
    pull_k8s_prod_env()
    click.echo('k8s production secrets have been pulled from Gitlab CI variable')


@gitlab.command()
@click.option('--user', prompt=True)
@click.option('--token', prompt=True)
def init(user, token):
    """Initialize the .devo/gitlab.yaml file to enable variable syncing"""
    data = {'gitlab_user': user,
            'gitlab_token': token}
    persist_gitlab_config(data)
    click.echo('gitlab.yaml initialized')

