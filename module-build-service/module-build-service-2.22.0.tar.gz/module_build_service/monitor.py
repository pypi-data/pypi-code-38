# -*- coding: utf-8 -*-
# Copyright (c) 2019  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# For an up-to-date version of this module, see:
#   https://pagure.io/monitor-flask-sqlalchemy

import os
import tempfile

from flask import Blueprint, Response
from prometheus_client import (  # noqa: F401
    ProcessCollector,
    CollectorRegistry,
    Counter,
    multiprocess,
    Histogram,
    generate_latest,
    start_http_server,
    CONTENT_TYPE_LATEST,
)
from sqlalchemy import event

# Service-specific imports
from module_build_service.utils import cors_header, validate_api_version


if not os.environ.get("prometheus_multiproc_dir"):
    os.environ.setdefault("prometheus_multiproc_dir", tempfile.mkdtemp())
registry = CollectorRegistry()
ProcessCollector(registry=registry)
multiprocess.MultiProcessCollector(registry)
if os.getenv("MONITOR_STANDALONE_METRICS_SERVER_ENABLE", "false") == "true":
    port = os.getenv("MONITOR_STANDALONE_METRICS_SERVER_PORT", "10040")
    start_http_server(int(port), registry=registry)


# Generic metrics
messaging_rx_counter = Counter(
    "messaging_rx", "Total number of messages received", registry=registry
)
messaging_rx_processed_ok_counter = Counter(
    "messaging_rx_processed_ok",
    "Number of received messages, which were processed successfully",
    registry=registry,
)
messaging_rx_failed_counter = Counter(
    "messaging_rx_failed",
    "Number of received messages, which failed during processing",
    registry=registry,
)

messaging_tx_to_send_counter = Counter(
    "messaging_tx_to_send", "Total number of messages to send", registry=registry
)
messaging_tx_sent_ok_counter = Counter(
    "messaging_tx_sent_ok", "Number of messages, which were sent successfully", registry=registry
)
messaging_tx_failed_counter = Counter(
    "messaging_tx_failed", "Number of messages, for which the sender failed", registry=registry
)

builder_success_counter = Counter(
    "builds_success", "Number of successful builds", registry=registry
)
builder_failed_counter = Counter(
    "builds_failed_total",
    "Number of failed builds",
    labelnames=["reason"],  # reason could be: 'user', 'infra', 'unspec'
    registry=registry,
)

db_dbapi_error_counter = Counter("db_dbapi_error", "Number of DBAPI errors", registry=registry)
db_engine_connect_counter = Counter(
    "db_engine_connect", "Number of 'engine_connect' events", registry=registry
)
db_handle_error_counter = Counter(
    "db_handle_error", "Number of exceptions during connection", registry=registry
)
db_transaction_rollback_counter = Counter(
    "db_transaction_rollback", "Number of transactions, which were rolled back", registry=registry
)

# Service-specific metrics
# XXX: TODO


def db_hook_event_listeners(target=None):
    # Service-specific import of db
    from module_build_service import db

    if not target:
        target = db.engine

    @event.listens_for(target, "dbapi_error", named=True)
    def receive_dbapi_error(**kw):
        db_dbapi_error_counter.inc()

    @event.listens_for(target, "engine_connect")
    def receive_engine_connect(conn, branch):
        db_engine_connect_counter.inc()

    @event.listens_for(target, "handle_error")
    def receive_handle_error(exception_context):
        db_handle_error_counter.inc()

    @event.listens_for(target, "rollback")
    def receive_rollback(conn):
        db_transaction_rollback_counter.inc()


monitor_api = Blueprint(
    "monitor", __name__, url_prefix="/module-build-service/<int:api_version>/monitor")


@cors_header()
@validate_api_version()
@monitor_api.route("/metrics")
def metrics(api_version):
    return Response(generate_latest(registry), content_type=CONTENT_TYPE_LATEST)
