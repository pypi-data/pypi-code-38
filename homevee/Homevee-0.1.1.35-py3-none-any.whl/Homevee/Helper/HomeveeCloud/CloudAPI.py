import json

import requests

from Homevee.Helper import Logger
from Homevee.Helper.Response import Response
from Homevee.Utils.Database import Database


class CloudAPI():
    def __init__(self, remote_id=None, access_token=None):
        db = Database()
        if remote_id is None:
            remote_id = db.get_server_data("REMOTE_ID")
        if access_token is None:
            access_token = db.get_server_data("REMOTE_ACCESS_TOKEN")
        self.remote_id = remote_id
        self.access_token = access_token
        self.url = "https://cloud.homevee.de"

    def do_post(self, path: str, params: dict, fields: list = None) -> Response:
        """
        Sends a post request to the CloudAPI
        :param path: the path to call
        :param params: the params
        :param fields: the fields
        :return: the response
        """
        try:
            body_data = json.dumps(params)
            headers = self.create_headers(body_data, fields)
            r = requests.post(self.url+path, data=body_data, headers=headers)
            return Response(r.status_code, r.content)
        except:
            #traceback.print_exc()
            return None

    def do_get(self, path: str, params: dict, fields: list = None) -> Response:
        """
        Sends a get request to the CloudAPI
        :param path: the path to call
        :param params: the params
        :param fields: the fields
        :return: the response
        """
        try:
            body_data = ""
            headers = self.create_headers(body_data, fields)
            r = requests.get(self.url+path, data=body_data, headers=headers)
            return Response(r.status_code, r.content)
        except:
            #traceback.print_exc()
            return None

    def do_delete(self, path: str, params: dict, fields: list = None) -> Response:
        """
        Sends a delete request to the CloudAPI
        :param path: the path to call
        :param params: the params
        :param fields: the fields
        :return: the response
        """
        try:
            body_data = json.dumps(params)
            headers = self.create_headers(body_data, fields)
            r = requests.delete(self.url+path, data=body_data, headers=headers)
            return Response(r.status_code, r.content)
        except:
            #traceback.print_exc()
            return None

    def do_put(self, path: str, params: dict, fields: list = None) -> Response:
        """
        Sends a put request to the CloudAPI
        :param path: the path to call
        :param params: the params
        :param fields: the fields
        :return: the response
        """
        try:
            body_data = json.dumps(params)
            headers = self.create_headers(body_data, fields)
            r = requests.put(self.url+path, data=body_data, headers=headers)
            return Response(r.status_code, r.content)
        except:
            #traceback.print_exc()
            return None

    def create_headers(self, body: str, fields: list = None) -> dict:
        """
        Creates the headers with the given fields
        :param body: the body
        :param fields: the fields of the header
        :return: the header dict
        """
        headers = {
            #"Host": self.url,
            "Connection": "keep-alive",
            "Content-Length": bytes(len(body)),
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.52 Safari/536.5",
            "Content-Type": "application/json",
            #"Accept": "*/*",
            #"Referer": "https://www.mywbsite.fr/data/mult.aspx",
            #"Accept-Encoding": "gzip,deflate,sdch",
            #"Accept-Language": "fr-FR,fr;q=0.8,en-US;q=0.6,en;q=0.4",
            #"Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
            "Remote-ID": self.remote_id,
            "Access-Token": self.access_token
        }
        if fields is not None:
            for key in fields:
                headers[key] = fields[key]
        if Logger.IS_DEBUG:
            print(headers)
        return headers