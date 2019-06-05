from __future__ import absolute_import, unicode_literals, print_function

import sys
import socket
import json
from ilabs.client.get_secret import get_secret
from ilabs.client.send_request import send_request, ILABS_USER_AGENT
from ilabs.client import __version__
import logging


def noop(*av, **kav): pass


class ILabsApi:

    URL_API_BASE = 'https://api.innodatalabs.com/v1'

    def __init__(self, user_key=None, timeout=None, user_agent=None):
        self.URL_PING     = self.URL_API_BASE + '/ping'

        self.URL_INPUT    = self.URL_API_BASE + '/documents/input/'
        self.URL_OUTPUT   = self.URL_API_BASE + '/documents/output/'
        self.URL_FEEDBACK = self.URL_API_BASE + '/documents/training/{domain}/'

        self.URL_PREDICT  = self.URL_API_BASE + '/reference/{domain}/{name}'
        self.URL_STATUS   = self.URL_API_BASE + '/reference/{domain}/{task_id}/status'
        self.URL_CANCEL   = self.URL_API_BASE + '/reference/{domain}/{task_id}/cancel'

        self.URL_PREDICT_DV  = self.URL_API_BASE + '/prediction/{domain}/{collection}/{name}'

        self._user_key = user_key or get_secret().get('ilabs_user_key')
        if self._user_key is None:
            raise RuntimeError('Could not find credentials')
        self._user_agent = user_agent or ILABS_USER_AGENT
        self._timeout = timeout
        if self._timeout is None:
            self._timeout = socket._GLOBAL_DEFAULT_TIMEOUT

    def _request(self, method, url, data=None, content_type=None, query=None):
        headers = {
            'User-Key'     : self._user_key,
            'User-Agent'   : self._user_agent,
            'Cache-Control': 'no-cache'
        }
        if content_type is not None:
            headers['Content-Type'] = content_type
        res = send_request(method, url,
            data=data,
            headers= headers,
            query=query
        )

        if res.getcode() not in (200, 202):
            raise RuntimeError('REST endpoint returned error: %s' % res.getcode())

        return res.read()

    def _post(self, url, data, content_type=None, query=None):
        return self._request('POST', url, data, content_type=content_type, query=query)

    def get(self, url, query=None):
        '''
        Issues GET request with credentials.
        Useful for status/ and cancel/ REST operations using
        urls returned from predict() call.
        '''
        return self._request('GET', url, query=query)

    def ping(self):
        '''
        Checks that API is accessible.

        Always returns this: { "ping": "pong" }.
        '''
        out = self.get(self.URL_PING)
        return json.loads(out.decode())

    def upload_input(self, binary_data, filename=None):
        '''
        Upload file to the input cloud folder as "filename".
        If "filename" is None, system will generate name for you.

        The best practice is to let system auto-generate name for you.

        Returns dictionary with the following keys:

        - bytes_accepted  - number of bytes in the uploaded file
        - input_filename  - the name of the file
        '''
        logging.info('Uploading as filename=%s', filename)
        url = self.URL_INPUT
        if filename:
            validate_filename(filename)
            url = self.URL_INPUT + filename
        out = self._post(url,
            data=binary_data,
            content_type='application/octet-stream')
        out = json.loads(out.decode())
        bytes_accepted = int(out['bytes_accepted'])
        if bytes_accepted != len(binary_data):
            raise RuntimeError('internal upload error: %r' % out)
        return out

    def download_input(self, filename):
        '''
        Downloads file from the input cloud folder.

        Returns binary contents of the file.
        '''
        logging.info('Downloading input: %s', filename)
        validate_filename(filename)
        return self.get(self.URL_INPUT + filename)

    def predict(self, domain, filename):
        '''
        Schedules a task to run prediction on file "filename" using
        domain "domain".

        Returns dictionary with the following keys:

        - task_id   - task id
        - task_cancel_url  - use this url to cancel the task
        - document_output_url - use this url to download prediction result
        - tast_status_url - query status
        - output_filename - name of the output file (created only after task
            successfully completes)
        - version - ???
        '''
        logging.info('Trigger prediction job: domain=%s, filename=%s', domain, filename)
        validate_filename(filename)
        url = self.URL_PREDICT.format(
            domain=domain,
            name=filename)
        out = self.get(url)
        return json.loads(out.decode())

    def predict_from_datavault(self, domain, collection, filename, input_facet='master', output_facet='prediction'):
        '''
        Schedules a task to run prediction on file "filename" using
        domain "domain".

        Returns dictionary with the following keys:

        - task_id   - task id
        - task_cancel_url  - use this url to cancel the task
        - document_output_url - use this url to download prediction result
        - tast_status_url - query status
        - output_filename - name of the output file (created only after task
            successfully completes)
        '''
        logging.info('Trigger prediction job from Datavault: domain=%s, name=%s/%s, input_facet=%s, output_facet=%s',
            domain, collection, filename, input_facet, output_facet)

        validate_filename(filename)
        url = self.URL_PREDICT_DV.format(
            domain=domain,
            collection=collection,
            name=filename)
        out = self._post(url, b'', query={
            'input_facet': input_facet,
            'output_facet': output_facet
        })
        return json.loads(out.decode())

    def status(self, domain, task_id):
        '''Query status of a task sceduled with predict() method

        It is recommended that clients use pre-built URL string
        returned by predict() call in 'task_status_url' to query
        the task status, instead of using this method.

        Returns dictionary with the following keys:

        - error - [optional] if present, indicates task execution error
        - completed - true or false. Typically client polls API until it
            sees compleded==True. This field is always present.
        - progress - number indicating current step
        - steps - estimated total number of steps in this task
        - message - [optional] contains progress message
        '''

        logging.info('Status query for job %s', task_id)

        url = self.URL_STATUS.format(
            domain=domain,
            task_id=task_id)
        out = self.get(url)
        return json.loads(out.decode())

    def cancel(self, domain, task_id):
        '''
        Cancel task scheduled with predict() method.

        It is recommended that clients use pre-built URL string
        returned by predict() call in 'task_cancel_url' to cancel
        the running task, instead of using this method.
        '''
        logging.info('Canceling job %s', task_id)

        url = self.URL_CANCEL.format(
            domain=domain,
            task_id=task_id)
        out = self.get(url)
        return json.loads(out.decode())

    def download_output(self, filename):
        '''
        Retrieves file from output cloud folder

        It is recommended that clients use pre-built URL string
        returned by predict() call in 'document_output_url' to retrieve
        the prediction result, instead of using this method.
        '''
        logging.info('Downloading output: %s', filename)
        validate_filename(filename)
        return self.get(self.URL_OUTPUT + filename)

    def upload_feedback(self, domain, filename, binary_data):
        '''
        Uploads file to training folder for the given "domain".
        Use it to provide prediction feedback like this:

        - send file for prediction
        - receive the prediction result
        - review predicted file and edit if necessary (to correct prediction mistakes)
        - upload to training folder using this method
        '''
        logging.info('Uploading feedback: domain=%s, filename=%s', domain, filename)

        validate_domain(domain)
        validate_filename(filename)
        url = self.URL_FEEDBACK.format(domain=domain) + filename
        out = self._post(url,
            data=binary_data,
            content_type='application/octet-stream')
        out = json.loads(out.decode())

        if out['bytes_accepted'] != len(binary_data):
            raise RuntimeError('internal upload error: %r' % out)

        return out

def validate_domain(domain):
    if '/' in domain or '..' in domain:
        raise ValueError('domain can not contain slashes nor double dots: %r' % domain)

def validate_filename(filename):
    if '/' in filename or '..' in filename:
        raise ValueError('file name can not contain slashes nor double dots: %r' % domain)
