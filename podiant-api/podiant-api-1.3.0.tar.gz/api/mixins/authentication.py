from api import utils
from importlib import import_module


class AuthenticationMixin(object):
    """
    View mixin that adds a helper method to retrieve authenticators.
    """

    def get_authenticators(self):
        """
        Helper method to return the authenticators for this view. If no
        ``authenticators`` property is defined, the default classes from
        ``settings.API_DEFAULT_AUTHENTICATORS`` are used.
        """

        if not hasattr(self, '_authenticator_cache'):
            if hasattr(self, 'authenticators'):
                self._authenticator_cache = [
                    a() for a in self.authenticators
                ]
            else:
                auths = []
                for auth in utils.get_authenticators():
                    module, klass = auth.rsplit('.', 1)
                    module = import_module(module)
                    klass = getattr(module, klass)
                    auths.append(
                        klass()
                    )

                self._authenticator_cache = auths

        return self._authenticator_cache
