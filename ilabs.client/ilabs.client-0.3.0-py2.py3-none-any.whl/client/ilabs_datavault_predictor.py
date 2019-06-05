from ilabs.client import ilabs_api, ilabs_datavault_api
import time
import json
import logging
import uuid

def noop(*av, **kav): pass


class ILabsDatavaultPredictor(ilabs_api.ILabsApi):

    @classmethod
    def init(cls, domain, collection, input_facet='input', output_facet='output', user_key=None, datavault_key=None, timeout=None, user_agent=None):
        return cls(
            ilabs_api.ILabsApi(user_key=user_key, timeout=timeout, user_agent=user_agent),
            ilabs_datavault_api.ILabsDatavaultApi(user_key=user_key, datavault_key=datavault_key, timeout=timeout, user_agent=user_agent),
            domain=domain,
            collection=collection,
            input_facet=input_facet,
            output_facet=output_facet
        )

    def __init__(self, api, datavault, domain, collection, input_facet='input', output_facet='output'):
        self.api = api
        self._datavault = datavault
        self._domain = domain
        self._collection = collection
        self._input_facet=input_facet
        self._output_facet=output_facet

    def __call__(self, binary_data, name=None, progress=None):
        if progress is None:
            progress = noop

        if name is None:
            name = str(uuid.uuid4())

        progress('uploading %s bytes' % len(binary_data))

        self.upload(binary_data, name, facet=self._input_facet)

        progress('uploaded')

        response = self.api.predict_from_datavault(self._domain, self._collection, name, input_facet=self._input_facet, output_facet=self._output_facet)
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
        prediction = self.download(name, facet=self._output_facet)
        progress('downloaded %s bytes' % len(prediction))

        return prediction

    def upload(self, binary_data, name, facet='master'):
        self._datavault.upload(binary_data, self._collection, name, facet=facet)

    def download(self, name, facet='master'):
        return self._datavault.download(self._collection, name, facet=facet)

    @property
    def datavault_api(self):
        return self._datavault

