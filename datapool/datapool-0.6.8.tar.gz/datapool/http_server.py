#! /usr/bin/env python
# encoding: utf-8
from __future__ import absolute_import, division, print_function

import atexit
import importlib
import json
import subprocess
# Copyright © 2018 Uwe Schmitt <uwe.schmitt@id.ethz.ch>
from contextlib import contextmanager
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from threading import Thread

from prometheus_client.exposition import MetricsHandler

from .logger import get_cmdline_logger, logger, setup_logger


def _get_logs(n):
    p = subprocess.Popen(
        "journalctl -u {name} -n {n}".format(name=__package__, n=n),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
    )
    output = p.stdout.readlines()
    return output


@contextmanager
def patch_get_logs(function):
    globals()["_get_logs"] = function
    try:
        yield
    finally:
        globals()["_get_logs"] = _get_logs


def latest_logs(n=1000):
    output = _get_logs(n)
    # includes code to automatically scroll down in browser, incl.
    # scroll down after reload. see also
    # https://stackoverflow.com/questions/3664381
    result = b"""
    <html>
        <body>
            <pre>
            %s
            </pre>
            <div id="end" />
        </body>
 
        <script>
             window.onload = function() {
                    var element = document.getElementById("end");
                    element.scrollTop = element.scrollHeight;
                    element.scrollIntoView(false);
                    console.log(element);
                };
             window.onbeforeunload  = window.onload;
        </script>
    </html>
""" % (
        b"".join(output),
    )
    return result



class _Handler(BaseHTTPRequestHandler):

    registry = MetricsHandler.registry

    def __init__(self, *args, **kwargs):
        BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

    def do_GET(self):

        if self.path == "/metrics":
            return MetricsHandler.do_GET(self)

        elif self.path == "/logs":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(latest_logs())

        elif self.path.startswith("/logs/"):
            try:
                n = int(self.path.split("/")[2])
            except ValueError:
                self.send_response(400)
                self.end_headers()
                return
            self.send_response(200)
            self.end_headers()
            self.wfile.write(latest_logs(n))

        elif self.path == "/":

            version = importlib.import_module(__package__).__version__
            message = dict(status="alive", version=version, started=self.server.started)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(bytes(json.dumps(message), "utf-8"))

        else:
            self.send_error(404)

    def log_message(self, format_, *args):
        if args and isinstance(args[0], str):
            path = args[0].split(" ")[1]
            if path == "/metrics":
                return
            print(format_ % args)


class _ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    """Thread per request HTTP server."""

    # Make worker threads "fire and forget". Beginning with Python 3.7 this
    # prevents a memory leak because ``ThreadingMixIn`` starts to gather all
    # non-daemon threads in a list in order to join on them at server close.
    # Enabling daemon threads virtually makes ``_ThreadingSimpleServer`` the
    # same as Python 3.7's ``ThreadingHTTPServer``.
    daemon_threads = True

    def __init__(self, address, handler):
        HTTPServer.__init__(self, address, handler)
        self.started = str(datetime.now())


class DataPoolHttpServer:
    def __init__(self, port=8000):
        self.port = port
        self.thread = None
        self.httpd = None

    def start(self):
        server_address = ("", self.port)
        httpd = _ThreadingSimpleServer(server_address, _Handler)
        thread = Thread(target=httpd.serve_forever)
        thread.start()
        self.thread = thread
        self.httpd = httpd
        logger().info("started web server")

    def stop(self):
        if self.thread is None or self.httpd is None:
            raise RuntimeError("you must start server first.")

        if not self.thread.isAlive():
            raise RuntimeError("something went wrong when starting webserver.")

        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join()
        logger().info("web server shut down")


@contextmanager
def run_http_server_in_background(config_http_server, print_ok):
    port = config_http_server.port
    server = DataPoolHttpServer(port)

    print_ok("- start background http server on port {}".format(port))
    server.start()

    try:
        yield
    finally:
        print_ok("- stop http server")
        server.stop()
        print_ok("- stopped http server")
