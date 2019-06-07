import http.server
import socketserver
from urllib.parse import urlparse
from multiprocessing import Process
import os
import traceback
import re
import json

import nanome
from nanome.util import Logs

enable_logs = False

# Format, MIME type, Binary
Types = {
    "ico" : ("image/x-icon", True),
    "html" : ("text/html; charset=utf-8", False),
    "css" : ("text/css", False),
    "js" : ("text/javascript", False),
    "png" : ("image/png", True),
    "jpg" : ("image/jpeg", True),
    "" : ("text/plain", False) # Default
}

# Utility to get type specs tuple
def get_type(format):
    try:
        return Types[format]
    except:
        return Types[""]

# Class handling HTTP requests
class RequestHandler(http.server.BaseHTTPRequestHandler):
    # Utility function to set response header
    def _set_headers(self, code, type='text/html; charset=utf-8'):
        self.send_response(code)
        self.send_header('Content-type', type)
        self.end_headers()

    # Special GET case: get file list
    def _send_list(self):
        self._set_headers(200, 'application/json')
        response = dict()
        response['success'] = True
        response['file_list'] = []
        file_list = [filename for filename in os.listdir(".") if _WebLoaderServer.file_filter(filename)]
        for file in file_list:
            response['file_list'].append(file)
        self.wfile.write(json.dumps(response).encode("utf-8"))

    # Standard GET case: get a file
    def _try_get_resource(self, path):
        old_path = os.getcwd()
        try:
            path_list = list(filter(None, path.split("/")))
            for elem in path_list[:-1]: # Follow url path
                if elem == "..": # A minimum security
                    continue
                os.chdir(elem)
            file = path_list[-1]
            format = file.split(".")[-1]
            type_specs = get_type(format) # Get Mime type and if binary type
            if type_specs[1] == True: # If binary type, open file in binary mode
                f = open(file, 'rb')
            else:
                f = open(file, 'r')
        except:
            self._set_headers(404)
            os.chdir(old_path)
            return

        os.chdir(old_path)
        page = f.read()
        if type_specs[1] == True: # If binary type, don't try to decode page to str
            to_send = page
        else:
            to_send = page.encode("utf-8")
        self._set_headers(200, type_specs[0])
        self.wfile.write(to_send)
        f.close()

    # Called on GET request
    def do_GET(self):
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path
        except:
            pass

        if path == "/list":
            self._send_list()
            return

        if path == "/":
            path = "index.html"
        self._try_get_resource(path)

    def _send_json_success(self, code=200):
        self._set_headers(code, 'application/json')
        response = dict()
        response['success'] = True
        self.wfile.write(json.dumps(response).encode("utf-8"))

    def _send_json_error(self, code, message):
        response = dict()
        response['success'] = False
        response['error'] = message
        self._set_headers(code, 'application/json')
        self.wfile.write(json.dumps(response).encode("utf-8"))

    # Called on POST request
    def do_POST(self):
        try:
            content_len = int(self.headers.get('Content-Length'))
            body = self.rfile.read(content_len).decode("utf-8")

            # Parse multipart form
            body_arr = body.split("\n")[:-2]
        except:
            Logs.warning("Error trying to parse request:\n", traceback.format_exc())
            self._send_json_error(200, "Parsing problem")
            return

        i = 0
        while i < len(body_arr):
            try:
                m = re.search('filename="(.*)"', body_arr[i + 1])
                file_name = m.group(1)
                i += 4
                next_i = i
                while next_i + 1 < len(body_arr):
                    if len(body_arr[next_i]) == 0 or body_arr[next_i][-1] != '\r':
                        body_arr[next_i] += '\r'
                    if body_arr[next_i + 1].startswith("Content-") and body_arr[next_i].startswith("--"):
                        next_i -= 1
                        break
                    next_i += 1
                next_i += 1
                file_body = ("".join(body_arr[i:next_i]))[:-1]
                i = next_i
            except:
                Logs.warning("Error trying to parse request:\n", traceback.format_exc())
                self._send_json_error(200, "Parsing problem")
                return

            if file_name == "":
                continue

            # If file already exists
            if os.path.isfile(file_name):
                self._send_json_error(200, file_name + " already exists")
                return

            # If file is not supported
            if not _WebLoaderServer.file_filter(file_name):
                self._send_json_error(200, file_name + " format not supported")
                return

            # Create file
            f = open(file_name, "w")
            f.write(file_body)
            f.close()
        self._send_json_success()

    # Called on DELETE request
    def do_DELETE(self):
        file = ""
        try:
            parsed_url = urlparse(self.path)
            file = parsed_url.path[1:]
        except:
            Logs.warning("Error trying to parse request:\n", traceback.format_exc())
            self._send_json_error(200, "Parsing problem")
            return

        try:
            if file != "":
                if _WebLoaderServer.file_filter(file): # Make sure file to delete is a molecular file
                    os.remove(file)
        except:
            self._send_json_error(200, "Cannot find file to delete")
            return

        self._send_json_success()

    # Override to prevent HTTP server from logging every request if enable_logs is False
    def log_message(self, format, *args):
        if enable_logs:
            http.server.BaseHTTPRequestHandler.log_message(self, format, *args)

class _WebLoaderServer():
    def __init__(self, port):
        self.__process = Process(target=_WebLoaderServer._start_process, args=(port,))

    @staticmethod
    def file_filter(name):
        return name.endswith(".pdb") or name.endswith(".sdf") or name.endswith(".cif")

    def start(self):
        self.__process.start()

    @classmethod
    def _start_process(cls, port):
        dir = os.path.join(os.path.dirname(__file__), '_WebLoader')
        os.chdir(dir)
        server = socketserver.TCPServer(("", port), RequestHandler)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass