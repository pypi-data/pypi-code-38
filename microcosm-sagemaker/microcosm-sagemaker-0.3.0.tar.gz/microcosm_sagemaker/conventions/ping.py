"""
Ping controller.
"""
from marshmallow import Schema, fields
from microcosm_flask.conventions.base import Convention
from microcosm_flask.conventions.encoding import dump_response_data
from microcosm_flask.conventions.registry import response
from microcosm_flask.namespaces import Namespace
from microcosm_flask.operations import Operation


class PingSchema(Schema):
    """
    AWS health check.

    """
    status = fields.String()


class PingConvention(Convention):
    def configure_query(self, ns, definition):
        @self.add_route("/ping", Operation.Query, ns)
        @response(PingSchema())
        def ping_query():
            # NB: We have no internal consistency check, but we'll likely want to
            # add this & change the response status code accordingly
            # XXX At some point we may want to add the ability to register checks,
            # similar to how we do for the microcosm-flask health convention.
            response_data = dict(
                status="healthy",
            )
            return dump_response_data(PingSchema(), response_data, 200)


def configure_ping(graph):
    ns = Namespace(
        subject="ping",
        version=None
    )
    convention = PingConvention(graph)

    convention.configure(ns, query=tuple())
