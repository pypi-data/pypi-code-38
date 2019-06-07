from importlib import import_module
from api import utils


class AuthorisationMixin(object):
    """
    View mixin that adds a helper method to retrieve authorisers.
    """

    def get_authorisers(self):
        """
        Helper method to return the authorisers for this view. If no
        ``authorisers`` property is defined, the default classes from
        ``settings.API_DEFAULT_AUTHORISERS`` are used.
        """

        if not hasattr(self, '_authoriser_cache'):
            if hasattr(self, 'authorisers'):
                self._authoriser_cache = [
                    a(self) for a in self.authorisers
                ]
            else:
                auths = []
                for auth in utils.get_authorisers():
                    module, klass = auth.rsplit('.', 1)
                    module = import_module(module)
                    klass = getattr(module, klass)
                    auths.append(
                        klass(self)
                    )

                self._authoriser_cache = auths

        return self._authoriser_cache
