from thompcoutils.log_utils import get_logger
import urllib.request
import json
import ssl
import pprint
from werkzeug.exceptions import BadRequestKeyError


class MissingArgumentException(Exception):
    pass


class Server:
    @staticmethod
    def get_info(args, request):
        if args is None:
            args = []
        values = {}
        for arg in args:
            found = False
            if request.json is not None:
                try:
                    rtn[arg] = str(request.json[arg])
                    continue
                except BadRequestKeyError:
                    pass
            if not found:
                try:
                    values[arg] = str(request.args[arg])
                    continue
                except BadRequestKeyError:
                    pass
            if not found:
                try:
                    values[arg] = request.form.get(arg)
                    if values[arg] is not None:
                        continue
                except BadRequestKeyError:
                    pass
            if not found:
                try:
                    values[arg] = request.form[arg]
                    if values[arg] is not None:
                        continue
                except BadRequestKeyError:
                    pass
            if arg not in values:
                raise MissingArgumentException("argument '{}' not not found in {}".format(arg, request.url))
        return values


class Client:
    def __init__(self, host, port, page_root="", crt_file=None):
        logger = get_logger()
        self.host = host
        self.application_page = page_root
        self.port = port
        self.crt_file = crt_file
        logger.debug("host:{}, port:{}".format(host, port))
        if self.crt_file:
            http = "https"
        else:
            http = "http"
        if page_root is None:
            page_root = ""
        self.url = '{}://{}:{}/{}'.format(http, host, port, page_root)

    def send_curl(self, command, values):
        logger = get_logger()
        url = "{}/{}".format(self.url, command)
        logger.debug("Accessing URL: {}".format(url))
        req = urllib.request.Request(url)
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        json_data = json.dumps(values)
        json_data_bytes = json_data.encode('utf-8')  # needs to be bytes
        req.add_header('Content-Length', len(json_data_bytes))

        if self.crt_file:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.load_verify_locations(self.crt_file)
            rtn = urllib.request.urlopen(req, json_data_bytes, context=context)
        else:
            rtn = urllib.request.urlopen(req, json_data_bytes)
        data = json.load(rtn)
        return data, rtn
