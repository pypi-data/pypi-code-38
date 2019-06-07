import re
from functools import wraps
from http import HTTPStatus

import requests
from flask import current_app, g, jsonify, request

token_missing = {
    'description': 'Authentication token missing or incorrectly formatted.',
    'status': HTTPStatus.UNAUTHORIZED,
}
token_invalid = {
    'description': 'Authentication token invalid or expired.',
    'status': HTTPStatus.UNAUTHORIZED,
}
user_disabled = {
    'description': 'User account disabled.',
    'status': HTTPStatus.FORBIDDEN,
}
permission_denied = {
    'description': 'You do not have access to this resource.',
    'status': HTTPStatus.FORBIDDEN,
}
auth_error = {
    'description': 'An error occurred trying to authenticate.',
    'status': HTTPStatus.INTERNAL_SERVER_ERROR,
}


def error_response(error):
    return jsonify({'description': error['description']}), error['status']


class UnauthenticatedUser:
    role = None
    is_active = True


class AuthenticatedUser:
    id = None
    email = None
    first_name = None
    last_name = None
    default_time_zone = None
    time_zone_name = None
    password_reset_expires = None
    password_reset_url = None
    has_device = None
    status = None
    brandpanel_id = None
    is_admin = None
    is_superadmin = None
    is_pending = None
    job_title = None
    avatar_url = None
    organization = None
    brands = None
    accessible_brands = None
    permissions = None
    updated_at = None
    created_at = None

    def __init__(self, *initial_data, **kwargs):
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

    @property
    def role(self):
        if self.is_superadmin:
            return 'superadmin'
        if self.is_admin:
            return 'admin'
        return 'user'

    @property
    def is_active(self):
        return self.status == 0


class ApplicationUser:
    role = 'app'
    is_active = True


def get_user(app_token, validate_token_func):
    auth_header = request.headers.get('Authorization')
    if auth_header is None:
        g.user = UnauthenticatedUser()
        return

    match = re.match(r'^(Application|Token|Bearer):? (\S+)$', auth_header)
    if not match:
        return error_response(token_missing)
    method = match.group(1)
    token = match.group(2)

    # Application token
    # Note: 'Token' is deprecated - all applications should be updated to use 'Application'
    if method == 'Application' or method == 'Token':
        if token == app_token:
            g.user = ApplicationUser()
        else:
            return error_response(token_invalid)

    # Bearer token
    elif method == 'Bearer':
        user = validate_token_func(match.group(2))
        if not user:
            return error_response(token_invalid)
        g.user = user

    if not g.user.is_active:
        return error_response(user_disabled)


roles = {
    'user': 0,
    'admin': 1,
    'superadmin': 2,
    'app': 3,
}


def role_required(role):
    """
    Currently, the supported roles are:

    1. user
    2. admin
    3. superadmin
    4. app

    Roles are ordered from least to most privilege. Each role receives the permissions of the roles
    before it. Example:

    If role='user', users with 'user', 'admin', 'superadmin', or 'app' roles will be granted access.
    If role='superadmin', only users with 'superadmin' or 'app' roles will be granted access.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if isinstance(g.user, UnauthenticatedUser):
                return error_response(token_missing)

            if roles[g.user.role] < roles[role]:
                return error_response(permission_denied)

            return func(*args, **kwargs)
        return wrapper
    return decorator


def validate_token_using_api(token):
    auth_server = current_app.config['DH_POTLUCK_AUTH_API_URL']
    res = requests.get(auth_server + '/api/self',
                       headers={'Authorization': f'Bearer {token}',
                                'content-type': 'application/json'})
    if res.status_code == HTTPStatus.OK:
        res_json = res.json()
        return AuthenticatedUser(res_json)

    return None
