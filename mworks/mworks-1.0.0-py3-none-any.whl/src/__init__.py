import logging
from io import StringIO
from typing import Dict
from datetime import datetime
from flask import Response


STARTUP_TIME = datetime.utcnow()


def collect_monitoring_variables() -> Dict:
    return {
        'startup_time': STARTUP_TIME,
        'uptime': (datetime.utcnow() - STARTUP_TIME).total_seconds(),
    }


def enable_varz(app) -> None:
    @app.route('/varz')
    def get_varz():
        varz = collect_monitoring_variables()
        lines = [f"{key} {value}" for key, value in varz.items()]
        return Response('\n'.join(lines), mimetype='text/plain')


def enable_logz(app) -> None:
    stream = StringIO()
    log = logging.getLogger()
    handler = logging.StreamHandler(stream)
    log.addHandler(handler)

    @app.route('/logz')
    def get_logz():
        return stream.getvalue()


def enable_common_routes(app) -> None:
    enable_varz(app)
    enable_logz(app)
