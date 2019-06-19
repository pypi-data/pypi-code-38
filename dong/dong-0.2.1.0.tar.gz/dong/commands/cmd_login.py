import click

from tinynetrc import Netrc

import dong
import dong.httpclient as httpclient

def _save(email, password):
        netrc = Netrc()
        netrc[dong.SERVER_NAME] = {
            'login': email,
            'password': password
        }
        netrc.save()


def _login(username, password):
    r = httpclient.post('api/v1/login/', json={'email': username, 'password': password})
    if r.status_code == 200:
        print("👍 Login OK")

        password = r.json()['token']
        _save(
            email=username,
            password=password
        )
    else:
        print("😭 Login failed")


@click.command(help='Login with your credentials.')
@click.option('-u', '--username', prompt=True)
@click.option('-p', '--password', prompt=True, hide_input=True)
def command(username, password):
    _login(username, password)
