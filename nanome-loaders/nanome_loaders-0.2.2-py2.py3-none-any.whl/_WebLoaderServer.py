import urllib
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

class DataManager(object):
    def __init__(self):
        self.newline_length = 1
        self.data = bytes()
        self.boundary = None
        self.byte = 0
        self.file_name = ""
        self.body = bytes()

    def find_boundary(self):
        while not self.done():
            n = self.get_current()
            if n == 0x0A:
                self.newline_length = 1
                self.boundary = self.data[:self.byte]
                return
            if (n == 0x0D):
                self.newline_length = 2
                self.boundary = self.data[:self.byte]
                return
            self.move_next_utf8()

    def is_newline(self):
        result = False
        curr_byte = self.get_current()
        if (self.newline_length == 1):
            result = curr_byte == 0x0A
        elif (self.newline_length == 2):
            result = curr_byte == 0x0D 
            if (result):
                result = self.data[self.byte + 1] == 0x0A
        return result

    def find_newline(self):
        while(not self.is_newline()):
            self.move_next()

    def curr_index(self):
        return self.byte

    def get_current(self):
        return self.data[self.byte]

    def move_next(self):
        if (self.is_newline()):
            self.byte += self.newline_length
        else:
            self.byte +=1

    def move_next_utf8(self):
        n = self.get_current()
        if n < 0x80:
            self.byte += 1            
        elif n < 0xc0:
            self.byte += 1
        elif n < 0xe0:
            self.byte += 3
        else:
            self.byte += 4

    def done(self):
        return self.byte >= len(self.data)

    def split(self, start, end):
        return self.data[start:end]

# Class handling HTTP requests
class RequestHandler(http.server.BaseHTTPRequestHandler):
    # Utility function to set response header
    def _set_headers(self, code, type='text/html; charset=utf-8'):
        self.send_response(code)
        self.send_header('Content-type', type)
        self.end_headers()

    def _write(self, message):
        try:
            self.wfile.write(message)
        except:
            Logs.warning("Connection reset while responding", self.client_address)

    # Special GET case: get file list
    def _send_list(self):
        self._set_headers(200, 'application/json')
        response = dict()
        response['success'] = True
        response['file_list'] = []
        file_list = [filename for filename in os.listdir(".") if _WebLoaderServer.file_filter(filename)]
        for file in file_list:
            response['file_list'].append(file)
        self._write(json.dumps(response).encode("utf-8"))

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
        self._write(to_send)
        f.close()

    # Called on GET request
    def do_GET(self):
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            path = urllib.parse.unquote(path)
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
        self._write(json.dumps(response).encode("utf-8"))

    def _send_json_error(self, code, message):
        response = dict()
        response['success'] = False
        response['error'] = message
        self._set_headers(code, 'application/json')
        self._write(json.dumps(response).encode("utf-8"))

    # Called on POST request
    def do_POST(self):
        try:
            content_len = int(self.headers.get('Content-Length'))
            data = self.rfile.read(content_len)
        except:
            Logs.warning("Error trying to parse request:\n", traceback.format_exc())
            self._send_json_error(200, "Parsing problem")
            return

        data_manager = DataManager()
        data_manager.data = data
        data_manager.find_boundary()

        done = False
        while not done:
            RequestHandler.read_header(data_manager)
            RequestHandler.read_data(data_manager)
            done = RequestHandler.check_EOF(data_manager)

            file_name = data_manager.file_name
            file_body = data_manager.body

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
            f = open(file_name, "wb")
            f.write(file_body)
            f.close()
        self._send_json_success()

    @classmethod
    def read_file_name(cls, data):
        header = data.decode("utf-8")
        m = re.search('filename="(.*)"', header)
        return m.group(1)

    #looks for 2 newlines in a row. This marks the end of a header
    @classmethod
    def skip_header(cls, data_manager):
        curr = False
        last = False
        while (True):
            data_manager.move_next()
            curr = data_manager.is_newline()
            if (curr and last):
                data_manager.move_next()
                return
            last = curr

    @classmethod
    def read_header(cls, data_manager):
        start = data_manager.curr_index()
        cls.skip_header(data_manager)
        end = data_manager.curr_index()
        header = data_manager.split(start, end)
        data_manager.file_name = cls.read_file_name(header)

    #returns whether or not the current character is the beggining of the first line of the header
    @classmethod
    def is_header(cls, data_manager):
        curr_index = data_manager.curr_index()
        boundary = data_manager.boundary
        #increment by 1 so we don't compare the newline itself
        header_l = data_manager.split(curr_index + data_manager.newline_length, curr_index + data_manager.newline_length + len(boundary))
        return boundary == header_l

    #looks for header
    @classmethod
    def skip_data(cls, data_manager):
        while (True):
            data_manager.find_newline()
            if (cls.is_header(data_manager)):
                return
            data_manager.move_next()

    @classmethod
    def read_data(cls, data_manager):
        start = data_manager.curr_index()
        cls.skip_data(data_manager)
        end = data_manager.curr_index()
        data_manager.body = data_manager.split(start, end)

    @classmethod
    def check_EOF(cls, data_manager):
        #read the newline before the boundary
        data_manager.move_next()
        #read the boundary
        for _ in range(len(data_manager.boundary)):
            data_manager.move_next()
        #check for EOF
        return not data_manager.is_newline()

    # Called on DELETE request
    def do_DELETE(self):
        file = ""
        try:
            parsed_url = urlparse(self.path)
            file = parsed_url.path[1:]
            file = urllib.parse.unquote(file)
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
        return name.endswith(".pdb") or name.endswith(".sdf") or name.endswith(".cif") or name.endswith(".ppt") or name.endswith(".pptx") or name.endswith(".pdf")

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