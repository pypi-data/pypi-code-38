import base64
import datetime
import hmac
import json
import pprint
import requests

from collections import namedtuple
from hashlib import sha512
from urllib.parse import urlparse
from urllib.parse import urlunparse

from requests import Request
from requests import Session

from .exceptions import APIUsageException


Endpoint = namedtuple('Endpoint', ['path', 'method'])

PING = Endpoint(path='/ping', method='GET')

BATCH_INFO = Endpoint(path='/batch', method='GET')
BATCH_CREATE = Endpoint(path='/batch', method='POST')
JOB_INFO = Endpoint(path='/job', method='GET')

DATASET = Endpoint(path='/data', method='POST')
DATASET_SUMMARY = Endpoint(path='/data/%s', method='GET')
SHARD = Endpoint(path='/data/%s/shard/%s', method='POST')
JOB_CANCEL = Endpoint(path='/job/%s', method='DELETE')
BATCH_CANCEL = Endpoint(path='/batch/%s', method='DELETE')

MODEL_DOWNLOAD = Endpoint(path='/model/%s/%s', method='GET')


class AbstractRequest(object):
    def __init__(self, options, *args, **kwargs):
        api_url = options.get('api_url')
        url_params = urlparse(api_url)
        if not url_params[0]:
            raise APIUsageException('api_url requires a scheme e.g. http')

        self.scheme = url_params[0]
        self.netloc = url_params[1]

        self.secret = options.get('secret', '')
        self.api_key = options.get('api_key', '')

        self.body = None

    def generate_sha512_hmac(self, secret, method, endpoint, payload):
        base_sig = '%s\n%s\n%s' % (method, endpoint, payload)
        return hmac.new(
            secret.encode('utf-8'),
            bytes(base_sig.encode('utf-8')),
            digestmod=sha512
        ).hexdigest()

    def get_headers(self, endpoint, payload):
        if not self.secret:
            print('WARNING: API key and/or secret not set')
            return {}

        signature = self.generate_sha512_hmac(
            self.secret,
            endpoint.method,
            endpoint.path,
            payload
        )

        return {
            'X-singularity-apikey': self.api_key,
            'X-singularity-signature': signature,
        }

    def send_request(self, endpoint, payload='', headers=None):
        url = urlunparse((
            self.scheme,
            self.netloc,
            endpoint.path,
            '',
            '',
            ''
        ))

        headers = headers or {}
        request = Request(endpoint.method, url, data=payload, headers=headers)

        try:
            response = Session().send(request.prepare())
        except requests.exceptions.ConnectionError:
            raise APIUsageException('Unable to establish connection with API')
        else:
            return response

    def handle_response(self):
        payload = {}
        try:
            payload = self.response.json()
        except ValueError:
            pass

        self.body = payload
        return self.body

    def request(self, endpoint, payload=''):
        self.endpoint = endpoint

        headers = self.get_headers(endpoint, payload)
        self.response = self.send_request(
            endpoint,
            payload=payload,
            headers=headers,
        )

        self.trace = self.response.headers.get('X-atlas-trace', '')
        return self.handle_response(), self.response.status_code

    def summary(self):
        print('[%d][%s][%s]' % (self.response.status_code, self.endpoint.path, self.trace))
        if self.body:
            pprint.PrettyPrinter(indent=4).pprint(self.body)


class Ping(AbstractRequest):

    def handle_response(self):
        content = self.response.content.decode('utf-8')
        if content == 'null':
            content = ''

        return content

    def run(self):
        return self.request(PING)

    def summary(self):
        super().summary()
        pprint.PrettyPrinter(indent=4).pprint(self.response.content.decode('utf-8'))


class BatchCreate(AbstractRequest):

    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)
        self.job_payload = options.get('payload', '')
        if not self.job_payload:
            raise APIUsageException('Need jobs to create a batch!')

        self.mode = options.get('mode', '')
        if not self.mode:
            raise APIUsageException('Mode must be set to either Pilot or Production')

        cpus = options.get('cpus') or '0'
        try:
            float(cpus)
        except ValueError():
            raise SystemExit('CPUs must be an integer number')

        self.cpus = float(cpus)

        gpus = options.get('gpus') or '0'
        try:
            float(gpus)
        except ValueError():
            raise SystemExit('GPUs must be an integer number')

        self.gpus = float(gpus)

    def run(self):
        payload = json.dumps({
            'mode': self.mode,
            'jobs': self.job_payload,
            'requisitions': {'cpu': self.cpus, 'gpu': self.gpus}
        })

        return self.request(BATCH_CREATE, payload)


class BatchStatus(AbstractRequest):

    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)

        self.endpoint = BATCH_INFO

        batch_uuid = options.get('uuid')
        if batch_uuid:
            self.endpoint = Endpoint(path='/batch/%s' % batch_uuid, method='GET')

    def run(self):
        return self.request(self.endpoint)


class BatchSummary(AbstractRequest):

    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)

        self.endpoint = BATCH_INFO

        self.since = None
        since = options.get('since')
        if since:
            self.since = datetime.datetime.strptime(since, '%Y-%m-%d')

    def run(self):
        return self.request(self.endpoint)

    def summary(self):
        print('[%d][%s][%s]' % (self.response.status_code, self.endpoint.path, self.trace))

        if self.body:
            for batch in self.body:
                batch_uuid = batch.get('uuid', '')
                status = batch.get('status', '')
                started = batch.get('created_at', '')
                if not self.since:
                    print('%s %s: %s' % (batch_uuid, started, status))
                    continue

                started_datetime = datetime.datetime.strptime(started, '%Y-%m-%dT%H:%M:%S.%fZ')
                if started_datetime >= self.since:
                    print('%s %s: %s' % (batch_uuid, started, status))


class JobStatus(AbstractRequest):

    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)

        self.endpoint = JOB_INFO

        uuid = options.get('uuid')
        if uuid:
            self.endpoint = Endpoint(path='/job/%s' % uuid, method='GET')

    def run(self):
        return self.request(self.endpoint)


class Cancel(AbstractRequest):
    def __init__(self, options, kind, **kwargs):
        super().__init__(options, kind, **kwargs)

        self.kind = kind
        self.uuid = options.get('uuid')

    def run(self):
        if self.kind == 'batch':
            path = BATCH_CANCEL.path % self.uuid
        elif self.kind == 'job':
            path = JOB_CANCEL.path % self.uuid

        endpoint = Endpoint(path=path, method='DELETE')

        return self.request(endpoint)


class DataSetAdd(AbstractRequest):
    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)

        self.name = options.get('name')

        pilot_count = options.get('pilot_count', 0)
        if not pilot_count:
            raise APIUsageException('Pilot Count not defined')

        if not pilot_count.isdigit():
            raise APIUsageException('Pilot Count must be an integer')

        self.pilot_count = int(pilot_count)

        self.dataset_endpoint = DATASET

    def run(self):
        request_payload = json.dumps({
            'name': self.name,
            'pilot_count': self.pilot_count
        })

        return self.request(self.dataset_endpoint, request_payload)


class ShardAdd(AbstractRequest):
    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)
        self.data_set_uuid = options.get('data_set_uuid')
        self.shard_id = options.get('shard_id')
        self.shard = options.get('shard')

    def run(self):
        shard_path = SHARD.path % (self.data_set_uuid, self.shard_id)
        endpoint = Endpoint(path=shard_path, method='POST')

        return self.request(endpoint, base64.b64encode(self.shard).decode())


class DataSetSummary(AbstractRequest):
    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)

        self.name = options.get('name')

    def run(self):
        path = DATASET_SUMMARY.path % self.name
        endpoint = Endpoint(path=path, method='GET')

        return self.request(endpoint)


class ModelDownload(AbstractRequest):
    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)

        self.batch_uuid = options.get('batch_uuid')
        self.job_uuid = options.get('job_uuid')

    def handle_response(self):
        return self.response.content

    def run(self):
        path = MODEL_DOWNLOAD.path % (self.batch_uuid, self.job_uuid)
        endpoint = Endpoint(path=path, method='GET')

        return self.request(endpoint)
