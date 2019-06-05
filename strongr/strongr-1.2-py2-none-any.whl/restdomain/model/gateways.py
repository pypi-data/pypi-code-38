import dependency_injector.containers as containers
import dependency_injector.providers as providers
from flask import Flask

from werkzeug.security import generate_password_hash, check_password_hash

from authlib.flask.oauth2 import AuthorizationServer, ResourceProtector
from strongr.restdomain.api.apiv1 import blueprint as apiv1
from strongr.restdomain.model.oauth2 import Token

from strongr.restdomain.model.oauth2.client import Client

import strongr.core
from strongr.restdomain.model.oauth2.endpoints.revocationendpoint import RevocationEndpoint
from strongr.restdomain.model.oauth2.grants.authorizationcodegrant import AuthorizationCode
from strongr.restdomain.model.oauth2.grants.clientcredentialsgrant import ClientCredentialsGrant
from strongr.restdomain.model.oauth2.grants.passwordgrant import PasswordGrant

class Gateways(containers.DeclarativeContainer):
    """IoC container of gateway objects."""
    _blueprints = providers.Object([apiv1])

    def _factor_app(name, blueprints):
        app = Flask(__name__)

        config = strongr.core.Core.config()
        backend = config.restdomain.backend.strip().lower()

        # the oauth2 lib can not work with templates,
        # this hack was proposed as a temp fix on the
        # libraries github. Use this for now, we
        # should refactor this later.
        # https://github.com/lepture/flask-oauthlib/issues/180
        #from strongr.restdomain.api.oauth2 import bind_oauth2
        #oauth2 = bind_oauth2(app)
        #app.oauth2 = oauth2

        for blueprint in blueprints:
            app.register_blueprint(blueprint)

        #auth_server = AuthorizationServer(Client, app)

        #auth_server.register_grant_endpoint(AuthorizationCode)
        #auth_server.register_grant_endpoint(PasswordGrant)
        #auth_server.register_grant_endpoint(ClientCredentialsGrant)

        #auth_server.register_revoke_token_endpoint(RevocationEndpoint)

        #Gateways.auth_server.override(auth_server)

        if backend == 'flask':
            flask_config = config.restdomain.flask.as_dict() if hasattr(config, 'restdomain') and hasattr(config.restdomain, 'flask') else {}
            # monkey patch run method so that config is grabbed from config file
            setattr(app, '_run_original', app.run)
            app.run = lambda self=app: self._run_original(**flask_config)
            return app
        elif backend == 'gunicorn':
            from gunicorn.app.base import BaseApplication

            # put WSGIServer class here for now
            # this should be refactored later
            class WSGIServer(BaseApplication):
                def __init__(self, app):
                    self.application = app
                    super(WSGIServer, self).__init__("%(prog)s [OPTIONS]")

                def load_config(self):
                    for key in config.restdomain.gunicorn.as_dict():
                        self.cfg.set(key, config.restdomain.gunicorn.as_dict()[key])

                def load(self):
                    return self.application

            return WSGIServer(app)

    @classmethod
    def _query_token(self, access_token):
        from authlib.flask.oauth2 import current_token
        import strongr.core.gateways

        return strongr.core.gateways.Gateways.sqlalchemy_session().query(Token).filter_by(access_token=access_token).first()


    def _factor_require_oauth():
        return ResourceProtector(Gateways._query_token)

    flask_app = providers.Singleton(_factor_app, 'StrongRRestServer', _blueprints())
    auth_server = providers.Configuration('auth_server') # initialized by _factor_app factory
    #current_user = providers.Factory(_factor_current_user)
    require_oauth = providers.Factory(_factor_require_oauth)

    generate_password_hash = providers.Factory(generate_password_hash, method='pbkdf2:sha256:80000', salt_length=8)
    check_password_hash = providers.Factory(check_password_hash)
