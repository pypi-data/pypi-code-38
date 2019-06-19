import click

from dong import auth
from dong import net
from dong import httpclient

def _bring_up(password, job_name):
    headers = net.authorization_headers(password)
    r = httpclient.post('api/v1/endpoint/', json={'job': job_name}, headers=headers)
    if r.status_code != 200:
        return None
    result = r.json()
    return result['endpoint_name']


@click.group()
def command():
    """Operate on endpoint."""
    pass


@command.command()
@click.argument('job_name')
def up(job_name):
    """Bring up endpoint to serve."""
    (login, password) = auth.get_credential_or_exit()

    print('Bring up...')
    endpoint = _bring_up(password, job_name)
    if endpoint is None:
        print("Can't bring up endpoint, stopped.")
        return
    click.echo('New endpoint name: ' + click.style(endpoint, fg='bright_green'))


@command.command()
@click.option('-e', '--endpoint-name')
def status(endpoint_name):
    """Retrieve endpointß status."""

    (login, password) = auth.get_credential_or_exit()
    headers = net.authorization_headers(password)
    try:
        r = httpclient.get('api/v1/endpoint/{}/'.format(endpoint_name), headers=headers)
        result = r.json()

        click.echo('Endpoint name: ' + click.style(result['name'], fg='bright_green'))
        click.echo('External ip: ' + click.style(result['external_ip'], fg='bright_green'))
        click.echo('Status: ' + click.style(result['status'], fg='bright_green'))
    except Exception as e:
        print("Can't get any status of endpoint: {}, stopped.".format(endpoint_name))


@command.command()
@click.option('-e', '--endpoint-name')
def kill(endpoint_name):
    """kill running endpoint."""

    (login, password) = auth.get_credential_or_exit()
    headers = net.authorization_headers(password)
    try:
        r = httpclient.post('api/v1/endpoint/{}/kill'.format(endpoint_name), headers=headers)
        result = r.json()
        print("success")
    except Exception as e:
        print("fail to kill {}".format(endpoint_name))
