#!/bin/env python3
import logging
import yaml
import os
import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.template
import tornado.websocket
import json

import mywebapp.webapp

logger = logging.getLogger(__name__)

# WEBSOCKET


class WSHandler(tornado.websocket.WebSocketHandler):

    def open(self):
        def callback():
            self.tick()
        self.pc = tornado.ioloop.PeriodicCallback(callback, 100.0)
        self.pc.start()
        self.command = None

    def on_message(self, message):
        self.command = message

    def tick(self):
        if not self.command:
            return
        event = {"body": self.command}
        self.write_message(json.dumps(event))
        self.command = None


# REST API Handlers


class API(tornado.web.RequestHandler):

    def initialize(self, api):
        self.api = api

    def json(self, obj):
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(obj))


# View Handlers


class View(tornado.web.RequestHandler):

    def initialize(self, api):
        self.api = api


class ViewApi(View):

    def get(self):
        self.render("api.html")


class ViewMain(View):

    def get(self):
        self.render("main.html")


def make_app(settings):
    api = mywebapp.webapp.API()

    handlers = [
        # static
        (r'/static/.*', tornado.web.StaticFileHandler, {'path': settings['static_path']}),

        # api
        (r"/api/.*", ViewApi, {"api": api}),

        # websockets
        (r'/ws/.*', WSHandler),

        # webpages
        (r"/.*", ViewMain, {"api": api}),
    ]

    return settings['port'], tornado.web.Application(handlers, **settings), api


if __name__ == "__main__":
    settings = yaml.load(open('website/conf/website.yaml').read())

    level = logging.DEBUG if settings['debug'] else logging.WARN
    logging.basicConfig(level=level,
                        format="%(levelname)8s %(asctime)s %(funcName)20s:%(lineno)-5d %(message)s",
                        datefmt='%a, %d %b %Y %H:%M:%S')

    port, app, api = make_app(settings)
    server = tornado.httpserver.HTTPServer(app)
    server.listen(port)
    api.register_server(server)
    logger.info("Listening on 0.0.0.0:{}".format(port))
    tornado.ioloop.IOLoop.current().start()
