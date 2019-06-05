from __future__ import absolute_import, unicode_literals

from ilabs.client import ilabs_api
import time
import json
import logging

def noop(*av, **kav): pass


class ILabsPredictor(ilabs_api.ILabsApi):

    @classmethod
    def init(cls, domain, *av, **kav):
        return cls(ilabs_api.ILabsApi(*av, **kav), domain)

    def __init__(self, api, domain):
        self.api = api
        self._domain = domain

    def __call__(self, binary_data, progress=None):
        if progress is None:
            progress = noop

        progress('uploading %s bytes' % len(binary_data))

        response = self.api.upload_input(binary_data)
        bytes_accepted = int(response['bytes_accepted'])
        input_filename = response['input_filename']
        progress('uploaded, accepted size=%s' % bytes_accepted)

        response = self.api.predict(self._domain, input_filename)
        task_id = response['task_id']
        task_cancel_url = response['task_cancel_url']
        document_output_url = response['document_output_url']
        task_status_url = response['task_status_url']
        output_filename = response['output_filename']
        progress('job submitted, taks id: %s' % task_id)

        try:
            count = 1
            for _ in range(100):
                for count_idx in reversed(range(count)):
                    time.sleep(1.0)
                    progress('retrying in: %s' % (count_idx+1))

                logging.info('Requesting status at %s', task_status_url)
                response = self.api.get(task_status_url)
                out = json.loads(response.decode())
                assert out is not None, response
                progress('progress: %s/%s' % (out['progress'], out['steps']))
                if out['completed']:
                    break
                count = min(count*2, 60)
            else:
                raise RuntimeError('timeout')

            task_cancel_url = None
        finally:
            if task_cancel_url is not None:
                logging.info('Cancelling job at %s', task_cancel_url)
                self.api.get(task_cancel_url)

        err = out.get('error')
        if err is not None:
            raise RuntimeError('Prediction server returned error: ' + err)

        progress('fetching result')
        logging.info('Downloading from: %s', document_output_url)
        prediction = self.api.get(document_output_url)
        progress('downloaded %s bytes' % len(prediction))

        return prediction

    def upload_feedback(self, filename, binary_data):
        return self.api.upload_feedback(self._domain, filename, binary_data)
