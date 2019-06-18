"""
Provide a basic set of endpoints for an application to implement OAuth client
functionality.

These endpoints assume that the ``current_app`` has already been configured
with an OAuth client instance from the ``authlib`` package as follows:

.. code-block:: python

    from authutils.oauth2.client import OAuthClient
    from service.api import app

    app.oauth_client = OAuthClient(
        'client-id',
        client_secret='...',
        api_base_url='https://api.auth.net/',
        access_token_url='https://auth.net/oauth/token',
        authorize_url='https://auth.net/oauth/authorize',
        client_kwargs={
            'scope': 'openid data user',
            'redirect_uri': 'https://service.net/authorize',
        },
    )

(NOTE the scopes are space-separated.)
"""

from urlparse import urljoin

from cdiserrors import APIError
import flask
from flask import current_app

import authutils.oauth2.client.authorize


blueprint = flask.Blueprint("oauth", __name__)


@blueprint.route("/authorization_url", methods=["GET"])
def get_authorization_url():
    """
    Provide a redirect to the authorization endpoint from the OP.
    """
    # This will be the value that was put in the ``client_kwargs`` in config.
    redirect_uri = current_app.oauth_client.session.redirect_uri
    # Get the authorization URL and the random state; save the state to check
    # later, and return the URL.
    authorization_url, state = current_app.oauth_client.generate_authorize_redirect(
        redirect_uri
    )
    flask.session["state"] = state
    return authorization_url


@blueprint.route("/authorize", methods=["GET"])
def do_authorize():
    """
    Send a token request to the OP.
    """
    authutils.oauth2.client.authorize.client_do_authorize()
    return "", 204


@blueprint.route("/logout", methods=["GET"])
def logout_oauth():
    """
    Log out the user.

    To accomplish this, just revoke the refresh token if provided.
    """
    url = urljoin(current_app.config.get("USER_API"), "/oauth2/revoke")
    token = flask.request.form.get("token")
    try:
        current_app.oauth_client.session.revoke_token(url, token)
    except APIError as e:
        msg = "could not log out, failed to revoke token: {}".format(e.message)
        return msg, 400
    return "", 204
