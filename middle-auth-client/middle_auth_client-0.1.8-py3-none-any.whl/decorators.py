from functools import wraps
import flask
import json
import os
import redis
from urllib.parse import quote

r = redis.Redis(
        host=os.environ.get('REDISHOST', 'localhost'),
        port=int(os.environ.get('REDISPORT', 6379)))

AUTH_URI = os.environ.get('AUTH_URI', 'localhost:5000/auth')


def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if hasattr(flask.g, 'auth_token'):
            # if authorization header has already been parsed, don't need to re-parse
            # this allows auth_required to be an optional decorator if auth_requires_role is also used
            return f(*args, **kwargs)

        token = None
        update_cookie = False
        cookie_name = 'middle_auth_token'

        auth_header = flask.request.headers.get('authorization')

        if auth_header or flask.request.environ.get('HTTP_ORIGIN'):
            if not auth_header:
                resp = flask.Response("Unauthorized", 401)
                resp.headers['WWW-Authenticate'] = 'Bearer realm="' + AUTH_URI + '"'
                return resp
            elif not auth_header.startswith('Bearer '):
                resp = flask.Response("Invalid Request", 400)
                resp.headers['WWW-Authenticate'] = 'Bearer realm="' + AUTH_URI + '", error="invalid_request", error_description="Header must begin with \'Bearer\'"'
                return resp

            token = auth_header.split(' ')[1] # remove schema
        else: # direct browser access, or a non-browser request missing auth header (user error) TODO: check user agent to deliver 401 in this case
            cookie_token = flask.request.cookies.get(cookie_name)
            query_param_token = flask.request.args.get('token')

            update_cookie = cookie_token != query_param_token # if token changes, update it

            token = query_param_token or cookie_token

            if not token:
                return flask.redirect('https://' + AUTH_URI + '/authorize?redirect=' + quote(flask.request.url), code=302)

        cached_user_data = r.get("token_" + token)

        if cached_user_data:
            flask.g.auth_user = json.loads(cached_user_data.decode('utf-8'))
            flask.g.auth_token = token
            resp = f(*args, **kwargs)

            if update_cookie:
                resp.set_cookie(cookie_name, token, secure=True, httponly=True)

            return resp
        else:
            resp = flask.Response("Invalid/Expired Token", 401)
            resp.headers['WWW-Authenticate'] = 'Bearer realm="' + AUTH_URI + '", error="invalid_token", error_description="Invalid/Expired Token"'
            return resp
    return decorated_function

def auth_requires_roles(*required_roles):
    def decorator(f):
        @wraps(f)
        @auth_required
        def decorated_function(*args, **kwargs):
            users_roles = flask.g.auth_user['roles']
            missing_roles = []

            for role in required_roles:
                if not role in users_roles:
                    missing_roles += [role]

            if missing_roles:
                resp = flask.Response("Missing role(s): {0}".format(missing_roles), 403)
                return resp
            else:
                return f(*args, **kwargs)

        return decorated_function
    return decorator

def auth_requires_roles_any(*required_roles):
    def decorator(f):
        @wraps(f)
        @auth_required
        def decorated_function(*args, **kwargs):
            users_roles = flask.g.auth_user['roles']

            for role in required_roles:
                if role in users_roles:
                    return f(*args, **kwargs)

            resp = flask.Response("Requires one of the following roles: {0}".format(list(required_roles)), 403)
            return resp
           
        return decorated_function
    return decorator
