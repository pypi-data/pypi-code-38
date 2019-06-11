import fcntl
import os
import re
import urllib
import errno
import json
import base64
import functools


class CassetteMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not os.getenv("CASSETTE_RECORDING", "0") == "1":
            return self.get_response(request)
        
        bulk_file_path = os.getenv("CASSETTE_BULK_FILE_PATH")
        bulk_file_separator = os.getenv("CASSETTE_BULK_FILE_SEPARATOR")


        request_body = self.parse_request_body(request)
        response = self.get_response(request)
        response_body = self.parse_response_body(response)

        request_headers = [ [self.normalize_header_key(k), str(v)] for (k,v) in request.META.items() if k == "CONTENT_TYPE" or (k != "HTTP_COOKIE" and k.startswith("HTTP_")) ]
        response_headers = [ [self.normalize_header_key(item[0]), str(item[1])] for item in list(response.items()) ]
        entry = {
            "path": request.path,
            "method": request.method,
            "status": response.status_code,
            "request_query": request.META.get("QUERY_STRING", None),
            "request_cookies": self.kv_list_to_dict(request.COOKIES.items()),
            "request_headers": self.kv_list_to_dict(request_headers),
            "request_body": request_body,
            "response_body": response_body,
            "response_headers": self.kv_list_to_dict(response_headers),
        }

        content = json.dumps(entry)
        try:
            with open(bulk_file_path, "a") as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                f.write(bulk_file_separator)
                f.write('\n')
                f.write(content)
                f.write('\n')
        except OSError as e:
            if (e.errno == errno.ENOENT):
                print("Could not write request blob to file. If this error persists use --bulk=false")

        return response

    def parse_request_body(self, request):
        return base64.b64encode(request.body).decode()

    def parse_response_body(self, response):
        return base64.b64encode(response.content).decode()

    def normalize_header_key(self, key):
        return re.sub('^http-', '', key.lower().replace("_", "-"))

    def kv_list_to_dict(self, kv_list):
        dct = {}
        for (key, value) in kv_list:
            dct.setdefault(key, [])
            dct[key].append(value)
        return dct
