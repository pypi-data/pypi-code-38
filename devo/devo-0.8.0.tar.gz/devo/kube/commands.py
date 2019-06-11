import click

from devo.config import read_config

from .utils import execute_tests, cleanup_test_env, init_kubectl, create_image_pull_secret, create_namespace


@click.group()
def kube():
    pass


@kube.command()
@click.option('--name')
@click.option('--url')
@click.option('--user')
@click.option('--token')
def init(name, url, user, token):
    """Initialize the kubeconfig to interact with a cluster via kubectl"""
    init_kubectl(name, url, user, token)


@kube.command()
@click.argument('namespace')
@click.option('--registry-user')
@click.option('--registry-password')
def prepare_env(namespace, registry_user, registry_password):
    """"Create a new namespace and add docker registry credentials as a secret"""
    config = read_config()
    registry_secret = config['project_name'] + '-registry'
    registry_url = config['registry']['url']
    create_namespace(namespace)
    create_image_pull_secret(namespace, registry_secret, registry_url, registry_user, registry_password)


@kube.command()
@click.argument('namespace', default='default')
@click.option('--timeout', default=300)
def test(namespace, timeout):
    """Run tests in a namespace"""
    execute_tests(namespace, timeout)


@kube.command()
@click.argument('namespace')
def after_test(namespace):
    """Delete a namespace and all its contents"""
    cleanup_test_env(namespace)

