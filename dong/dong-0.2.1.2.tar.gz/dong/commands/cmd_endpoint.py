import click

from dong import auth
from dong import net
from dong import httpclient


usage_tip = "\n[Usage] Status check:\ndong endpoint status -e {}\n"

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
    click.echo(
        "\n"
        + "New endpoint-name: " 
        + click.style(" {} ".format(endpoint), reverse=True) 
        + "\n"
        + usage_tip.format(endpoint)
        )


@command.command()
@click.option('-e', '--endpoint-name', required=True)
def status(endpoint_name):
    """Retrieve endpoint status."""

    (login, password) = auth.get_credential_or_exit()
    headers = net.authorization_headers(password)
    try:
        r = httpclient.get('api/v1/endpoint/{}/'.format(endpoint_name), headers=headers)
        result = r.json()

        click.echo('\nEndpoint name: ' + click.style(result['name'], fg='green'))
        click.echo('External ip: ' + click.style(result['external_ip'], fg='green'))
        click.echo('Status: ' + click.style(result['status'] + "\n"))
    except Exception as e:
        print("\nCan't get any status of endpoint: {}, stopped.\n".format(endpoint_name))


@command.command()
@click.option('-e', '--endpoint-name', required=True)
def kill(endpoint_name):
    """kill running endpoint."""
   
    (login, password) = auth.get_credential_or_exit()
    headers = net.authorization_headers(password)
    try:
        r = httpclient.post('api/v1/endpoint/{}/kill'.format(endpoint_name), headers=headers)
        result = r.json()
        print("{} ready to kill".format(endpoint_name))
        print(usage_tip.format(endpoint_name))  

    except Exception as e:
        print("fail to kill {}\n{}".format(endpoint_name),e)
