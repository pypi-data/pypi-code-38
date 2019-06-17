import json
from functools import wraps, partial
from flask import request, jsonify

from .auth import jwt_decode_auth_token


def authenticate(f=None, session=None, **kwargs):
    """
    :param f:
    :param session: a reference to redis db
    :return:
    """

    if f is None:
        return partial(authenticate, session=session, **kwargs)

    @wraps(f)
    def decorated_view(*args, **kwargs):
        response_object = {
            'status': False,
            'message': 'Provide a valid auth token.'
        }
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify(response_object), 401
        auth_token = auth_header.split(" ")[1]
        resp = jwt_decode_auth_token(auth_token)
        if isinstance(resp, str):
            response_object['message'] = resp
            return jsonify(response_object), 403
        if session:
            session_data = session.get(resp.get('id'))
            if session_data is None:
                response_object["message"] = "Authentication invalid"
                return jsonify(response_object), 401
            kwargs.update(dict(
                session_data=json.loads(session.get(resp.get('id'))))
            )
        kwargs.update(dict(resp=resp))
        return f(*args, **kwargs)
    return decorated_view
