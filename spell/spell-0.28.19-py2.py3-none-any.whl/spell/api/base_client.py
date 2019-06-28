# -*- coding: utf-8 -*-
from __future__ import print_function
import json
import posixpath

from dateutil.parser import isoparse
import requests

from spell.api import exceptions, models


SPELL_OBJ_HOOKS = {
    "billing_status": models.BillingStatus,
    "cpu_stats": models.CPUStats,
    "creator": models.User,
    "gpu_stats": [models.GPUStats],
    "hyper_search": models.HyperSearch,
    "key": models.Key,
    "keys": [models.Key],
    "log_entry": models.LogEntry,
    "ls": [models.LsLine],
    "managing_run": models.Run,
    "members": [models.OrgMember],
    "memberships": [models.OrgMember],
    "organization": models.Organization,
    "owner": models.Owner,
    "run": models.Run,
    "runs": [models.Run],
    "model_server": models.ModelServer,
    "model_servers": [models.ModelServer],
    "model_server_log_entry": models.ModelServerLogEntry,
    "template": models.Template,
    "user": models.User,
    "user_dataset": models.UserDataset,
    "workflow": models.Workflow,
    "workspace": models.Workspace,
    "workspaces": [models.Workspace],
}

SPELL_ENCODERS = [models.RunRequest, models.ValueSpec, models.RangeSpec, models.Environment, models.NameVersionPair]


class SpellDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super(SpellDecoder, self).__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        for k, v in obj.items():
            if k in SPELL_OBJ_HOOKS:
                spell_type = SPELL_OBJ_HOOKS[k]
                # Handle list-type objects
                if type(spell_type) == list and v is not None:
                    spell_type = spell_type[0]
                    try:
                        obj[k] = [spell_type(**spell_blob) for spell_blob in v]
                    except TypeError as e:
                        raise ValueError("{} ({})".format(e, obj))
                # Handle solo objects
                elif v is not None:
                    try:
                        obj[k] = spell_type(**v)
                    except TypeError as e:
                        raise ValueError("{} ({})".format(e, obj))
            elif is_likely_date(k):
                # Try date objects
                try:
                    obj[k] = isoparse(v)
                except (ValueError, TypeError):
                    pass

        # We did it!
        return obj


def is_likely_date(s):
    return (
        s in [
            "date",
            "last_logged_in",
            "last_start",
        ] or
        s.endswith("_at") or
        s.endswith("_date") or
        s.endswith("_time")
    )


class SpellEncoder(json.JSONEncoder):
    def default(self, obj):
        for encoder in SPELL_ENCODERS:
            if isinstance(obj, encoder):
                return obj.to_payload()
        return json.JSONEncoder.default(self, obj)


class JwtAuth(requests.auth.AuthBase):

    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["Authorization"] = "Bearer {}".format(self.token)
        return r


class BaseClient(object):

    def __init__(self, base_url, version_str, owner=None, token=None, adapter=None):
        self.base_url = base_url
        self.version_str = version_str
        self.owner = owner
        self.token = token
        self.session = requests.Session()
        if adapter:
            self.session.mount(self.base_url, adapter)

    def request(self, method, resource_url, headers=None, payload=None, params=None, stream=False, timeout=None):
        kwargs = {}
        kwargs["method"] = method
        kwargs["stream"] = stream
        kwargs["headers"] = {
            "Accept-Encoding": "gzip",
        }
        kwargs["url"] = posixpath.join(self.base_url, self.version_str, resource_url)
        if payload:
            kwargs["data"] = json.dumps(payload, cls=SpellEncoder)
            kwargs["headers"].update({"Content-Type": "application/json"})
        if headers:
            kwargs["headers"].update(headers)
        if params:
            kwargs["params"] = params
        if self.token:
            kwargs["auth"] = JwtAuth(self.token)
        if timeout:
            kwargs["timeout"] = timeout

        try:
            resp = self.session.request(**kwargs)
        except requests.ConnectionError:
            raise exceptions.ClientException(msg="Can't reach Spell. Please check your internet connection.")
        except requests.RequestException as e:
            raise exceptions.ClientException(msg=str(e), exception=e)
        return resp

    def check_and_raise(self, response):
        if response.status_code in (200, 201, 202, 204):
            return
        error = exceptions.decode_error(response)
        if response.status_code == 401:
            raise exceptions.UnauthorizedRequest(msg=str(error) if error else None, response=response)
        elif response.status_code == 400:
            raise exceptions.BadRequest(msg=str(error) if error else None, response=response)
        elif response.status_code == 409:
            raise exceptions.ConflictRequest(msg=str(error) if error else None, response=response)
        elif response.status_code == 500:
            raise exceptions.ServerError(msg=str(error) if error else None, response=response)
        else:
            raise exceptions.ClientException(msg=str(error) if error else None, response=response)

    def get_json(self, response):
        try:
            return json.loads(response.text, cls=SpellDecoder)
        except ValueError as e:
            message = "Error decoding the response: {}".format(e)
            raise exceptions.JsonDecodeError(msg=message, response=response, exception=e)
