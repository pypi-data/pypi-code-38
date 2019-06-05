from functools import wraps
import strongr.restdomain.model.gateways

# oauth2 lib does not support namespaces so we need a hack
# https://github.com/lepture/flask-oauthlib/issues/180
def namespace_require_oauth(*scopes):
    def wrapper(f):
        @wraps(f)
        def check_oauth(*args, **kwargs):
            return strongr.restdomain.model.gateways.Gateways.require_oauth()(*scopes)(f)(*args, **kwargs)

        return check_oauth
    return wrapper
