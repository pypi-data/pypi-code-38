from pkg_resources import resource_filename
from tornado.web import StaticFileHandler
from tornado.options import options
from .authentication.auth_static_file_handler import AuthStaticFileHandler
from .authentication import LogoutHandler
from .json_rpc2 import JsonRpcHandler
import importlib
import logging


def urls():
    static_dir = options.static_dir
    if static_dir is None:
        static_dir = resource_filename("bluemax.web", "static")
    logging.info("static_dir %s", static_dir)
    if options.auth_class:
        FileHandler = AuthStaticFileHandler
    else:
        FileHandler = StaticFileHandler
    result = [
        (r"/rpc", JsonRpcHandler),
        (r"/(.*)", FileHandler, {"path": static_dir, "default_filename": "index.html"}),
    ]
    if options.auth_class:
        module_name, class_name = options.auth_class.split(":")
        login_handler = getattr(importlib.import_module(module_name), class_name)
        result = [(r"/login", login_handler), (r"/logout", LogoutHandler)] + result
    return result
