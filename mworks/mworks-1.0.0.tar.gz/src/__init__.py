import logging
from io import StringIO
from typing import Dict, Optional
import mistune
from datetime import datetime
from flask import Response, Flask, send_file, abort
from prometheus_flask_exporter import PrometheusMetrics


class CommonRoutes:
    def __init__(self, app: Flask) -> None:
        self.app = app
        self.enable_varz()
        self.enable_healthz()
        self.enable_logz()
        self.enable_docz()

    def enable_varz(self) -> None:
        """ Enable a /varz route. It's used for monitoring and statistics.
        Varz is a standard path used by monitoring systems. This format is
        understood by standard software, like prometheus (or borgmon).
        Users of mworks can easily track their own variables:

        mworks = CommonRoutes(app)
        var = mworks.metrics.info('var_name', 'Var description')
        var.set(1337)
        """
        self.metrics = PrometheusMetrics(self.app, path='/varz')

    def enable_healthz(self) -> None:
        """ Enable a /healthz route. It's used for service health-checks.
        Healthz is a standard path used for service health checks. It should
        return HTTP 200 code if the application is healthy, and 500 otherwise.
        """
        def get_healthz():
            return ("ok", 200)

        self.app.route('/healthz')(get_healthz)

    def enable_logz(self) -> None:
        """ Enable a /logz route. It provides easy access to the service logs.
        Data in logs can be pretty senstive, so remember to restrict access to
        the intranet.
        """
        stream = StringIO()
        log = logging.getLogger()
        handler = logging.StreamHandler(stream)
        log.addHandler(handler)

        def get_logz():
            text = stream.getvalue()
            return Response(text, mimetype='text/plain')

        self.app.route('/logz')(get_logz)

    def enable_docz(self) -> None:
        """ Enable a /docz route. It provides easy access to the service logs.
        Data in logs can be pretty senstive, so remember to restrict access to
        the intranet.
        """
        def get_docz():
            readme_path = f"{self.app.root_path}/../README.md"
            try:
                with open(readme_path, "r") as readmef:
                    return mistune.markdown(readmef.read())
            except FileNotFoundError:
                abort(404)

        self.app.route('/docz')(get_docz)
