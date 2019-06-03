"""
This file contains a hack to make swagger-ui work from behind a load balancer.
It contains no application specific code and could have been a library.
"""
from flask_restplus import Api
from flask_restplus.api import SwaggerView


class CustomAPI(Api):
    """
    Hack to serve swagger.json from the /api prefix.  This is a requirement for
    serving swagger-ui from behind a path-routing load balancer without
    additional proxies.
    """

    def _register_specs(self, app_or_blueprint):
        if self._add_specs:
            endpoint = str('specs')
            self._register_view(
                app_or_blueprint,
                SwaggerView,
                self.default_namespace,
                '{}/swagger.json'.format(self.prefix),
                endpoint=endpoint,
                resource_class_args=(self, ))
            self.endpoints.add(endpoint)
