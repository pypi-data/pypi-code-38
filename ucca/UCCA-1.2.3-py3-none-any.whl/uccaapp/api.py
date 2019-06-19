from time import sleep

import json
import logging
import os
import requests

"""
API code for accessing v1.0 of the UCCAApp server
"""

DEFAULT_SERVER = "http://ucca-demo.cs.huji.ac.il"
API_PREFIX = "/api/v1/"
SERVER_ADDRESS_ENV_VAR = "UCCA_APP_SERVER_ADDRESS"
AUTH_TOKEN_ENV_VAR = "UCCA_APP_AUTH_TOKEN"
EMAIL_ENV_VAR = "UCCA_APP_EMAIL"
PASSWORD_ENV_VAR = "UCCA_APP_PASSWORD"
PROJECT_ID_ENV_VAR = "UCCA_APP_PROJECT_ID"
SOURCE_ID_ENV_VAR = "UCCA_APP_SOURCE_ID"
USER_ID_ENV_VAR = "UCCA_APP_USER_ID"
MAX_RETRIES = 3
RETRY_WAIT_DURATION = 60


class ServerAccessor:
    def __init__(self, server_address, email, password, auth_token=None, verbose=False, **kwargs):
        logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)
        server_address = server_address or os.environ.get(SERVER_ADDRESS_ENV_VAR, DEFAULT_SERVER)
        self.prefix = server_address + API_PREFIX
        self.headers = {}  # Needed for self.request (login)
        try:
            token = auth_token or os.environ.get(AUTH_TOKEN_ENV_VAR) or self.login(
                email or os.environ[EMAIL_ENV_VAR], password or os.environ[PASSWORD_ENV_VAR])["token"]
        except KeyError as e:
            raise ValueError("Must set either --auth-token, or --email and --password."
                             "Alternatively, set the %s environment variable, or %s and %s" %
                             (AUTH_TOKEN_ENV_VAR, EMAIL_ENV_VAR, PASSWORD_ENV_VAR)) from e
        self.headers["Authorization"] = "Token " + token
        self.source = self.project = self.layer = self.user = None

    def set_source(self, source_id=None):
        try:
            self.source = self.get_source(int(os.environ[SOURCE_ID_ENV_VAR]) if source_id is None else source_id)
        except KeyError as e:
            raise ValueError("Must set --source-id or the %s environment variable" % SOURCE_ID_ENV_VAR) from e

    def set_project(self, project_id=None):
        try:
            self.project = self.get_project(int(os.environ[PROJECT_ID_ENV_VAR]) if project_id is None else project_id)
        except KeyError as e:
            raise ValueError("Must set --project-id or the %s environment variable" % PROJECT_ID_ENV_VAR) from e
        self.layer = self.get_layer(self.project["layer"]["id"])

    def set_user(self, user_id=None):
        try:
            self.user = dict(id=int(os.environ[USER_ID_ENV_VAR]) if user_id is None else user_id)
        except KeyError as e:
            raise ValueError("Must set --user-id or the %s environment variable" % USER_ID_ENV_VAR) from e

    @staticmethod
    def add_arguments(argparser):
        argparser.add_argument("--server-address", help="UCCA-App server, otherwise set by " + SERVER_ADDRESS_ENV_VAR)
        argparser.add_argument("--email", help="UCCA-App email, otherwise set by " + EMAIL_ENV_VAR)
        argparser.add_argument("--password", help="UCCA-App password, otherwise set by " + PASSWORD_ENV_VAR)
        argparser.add_argument("--auth-token", help="authorization token (required only if email or password missing), "
                                                    "otherwise set by " + AUTH_TOKEN_ENV_VAR)
        argparser.add_argument("-v", "--verbose", action="store_true", help="detailed output")

    @staticmethod
    def add_source_id_argument(argparser):
        argparser.add_argument("--source-id", type=int, help="source id, otherwise set by " + SOURCE_ID_ENV_VAR)

    @staticmethod
    def add_project_id_argument(argparser):
        argparser.add_argument("--project-id", type=int, help="project id, otherwise set by " + PROJECT_ID_ENV_VAR)

    @staticmethod
    def add_user_id_argument(argparser):
        argparser.add_argument("--user-id", type=int, help="user id, otherwise set by " + USER_ID_ENV_VAR)

    def request(self, method, url_suffix, **kwargs):
        response = None
        for _ in range(MAX_RETRIES):
            response = requests.request(method, self.prefix + str(url_suffix), headers=self.headers, **kwargs)
            if response.status_code != 500:
                break
            sleep(RETRY_WAIT_DURATION)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise requests.exceptions.HTTPError(response.text) from e
        return response

    def login(self, email, password):
        return self.request("post", "login", json=dict(email=email, password=password)).json()

    @staticmethod
    def type(data):
        return data.get("type", "").lower()

    def update(self, data, prefix):
        logging.debug("Updating %s %s: %s" % (self.type(data), prefix, json.dumps(data)))
        out = self.request("put", prefix + "/%s/" % data["id"], json=data).json()
        logging.debug("Updated %s %s: %s" % (data.get("type", ""), prefix, json.dumps(out)))
        return out

    def create(self, data, prefix):
        logging.debug("Creating %s %s: %s" % (self.type(data), prefix, json.dumps(data)))
        out = self.request("post", prefix + "/", json=data).json()
        logging.debug("Created %s %s: %s" % (self.type(data), prefix, json.dumps(out)))
        return out

    def get(self, _id, prefix):
        logging.debug("Getting %s %s" % (prefix, _id))
        out = self.request("get", "%s/%s" % (prefix, _id)).json()
        logging.debug("Got %s: %s" % (prefix, json.dumps(out)))
        return out

    def submit_task(self, **kwargs):
        logging.debug("Submitting %s task: %s" % (self.type(kwargs), json.dumps(kwargs)))
        self.request("put", "user_tasks/%s/draft" % kwargs["id"], json=kwargs)
        out = self.request("put", "user_tasks/%s/submit" % kwargs["id"], json=kwargs).json()
        logging.debug("Submitted %s task: %s" % (self.type(kwargs), json.dumps(out)))
        return out

    def get_source(self, source_id):
        return self.get(source_id, prefix="sources")

    def get_project(self, project_id):
        return self.get(project_id, prefix="projects")

    def get_layer(self, layer_id):
        return self.get(layer_id, prefix="layers")

    def get_category(self, category_id):
        return self.get(category_id, prefix="categories")

    def create_category(self, **kwargs):
        return self.create(kwargs, prefix="categories")

    def get_user(self, user_id):
        return self.get(user_id, prefix="users")

    def get_task(self, task_id):
        return self.get(task_id, prefix="tasks")

    def create_task(self, **kwargs):
        return self.create(kwargs, prefix="tasks")

    def update_task(self, **kwargs):
        return self.update(kwargs, prefix="tasks")

    def get_user_task(self, task_id):
        return self.get(task_id, prefix="user_tasks")

    def get_passage(self, passage_id):
        return self.get(passage_id, prefix="passages")

    def create_passage(self, **kwargs):
        return self.create(kwargs, prefix="passages")

    def update_passage(self, **kwargs):
        return self.update(kwargs, prefix="passages")
