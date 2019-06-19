import json
import os, webbrowser
import random, threading, logging

import flask  # for temporary redirection server.
from flask import current_app, Blueprint, request, send_from_directory

# blueprint, which we register with temporary server app in Authorizer factory class.
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/authorize')
def authorize():
    print('\033[H\033[J')
    print('now complete authorisation in your web browser.')

    client_creds_path = current_app.config['client_creds_path']
    client_creds_json = json.loads(open(client_creds_path, 'rb').read().decode('utf-8'))
    authorization_endpoint_url = os.path.join(
        current_app.config['platform_url'],
        'accounts/v1/oauth/authorize'
    )
    authorization_endpoint_args = {
        "client_id": client_creds_json['client_id'],
        "response_type": "token",
        "scope": "vedavaapi.root",
        "redirect_uri": "http://localhost:{}/oauth_callback.html".format(current_app.config['port']),
        "state": "sample state"
    }
    args_string = '&'.join(['{}={}'.format(k, authorization_endpoint_args[k]) for k in authorization_endpoint_args])

    return flask.redirect(authorization_endpoint_url + '?' + args_string)


@auth_bp.route('/oauth_callback')
def oauth2callback():

    auth_creds_json = request.args.copy()
    credentials_file = open(current_app.config['authorized_creds_path'], 'wb')
    credentials_file.write(json.dumps(auth_creds_json, indent=2).encode('utf-8'))

    print('\033[H\033[J')
    print('authorization completed successfully, credentials stored in {}'.format(
        current_app.config['authorized_creds_path']))
    shutdown_server()
    return 'credentials successfully stored in {}'.format(current_app.config['authorized_creds_path'])


@auth_bp.route('/oauth_callback.html')
def oauth_callback_html():
    return send_from_directory('static', 'oauth_callback.html')

def shutdown_server():
    func = flask.request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


class Authorizer(object):

    def __init__(self, platform_url, client_creds_path, authorized_creds_path, scopes, port=6003, **kwargs):
        super(Authorizer, self).__init__()
        self.server_app = flask.Flask(__name__)
        self.server_app.secret_key = "somERandoMKey"

        self.server_app.config['platform_url'] = platform_url
        self.server_app.config['client_creds_path'] = client_creds_path
        self.server_app.config['authorized_creds_path'] = authorized_creds_path
        self.server_app.config['port'] = port
        self.server_app.config['scopes'] = scopes

        self.server_port = port

        self.server_app.register_blueprint(auth_bp)

    def authorize(self):
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        port = self.server_port
        url = 'http://localhost:{port}/authorize'.format(port=port)
        threading.Timer(1.25, lambda: webbrowser.open(url)).start()
        self.server_app.run(port=port, debug=False)



