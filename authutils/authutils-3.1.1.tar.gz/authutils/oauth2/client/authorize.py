from authlib.common.errors import AuthlibBaseError
import flask
from flask import current_app

from authutils.errors import AuthError
from authutils.token import store_session_token


def client_do_authorize():
    redirect_uri = current_app.oauth_client.session.redirect_uri
    mismatched_state = (
        "state" not in flask.request.args
        or "state" not in flask.session
        or flask.request.args["state"] != flask.session.pop("state")
    )
    if mismatched_state:
        raise AuthError("could not authorize; state did not match across auth requests")
    try:
        token = current_app.oauth_client.fetch_access_token(
            redirect_uri, **flask.request.args.to_dict()
        )
        store_session_token(token["access_token"])
        return token
    except KeyError as e:
        raise AuthError("error in token response: {}".format(token))
    except AuthlibBaseError as e:
        raise AuthError(str(e))
