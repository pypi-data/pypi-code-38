"""Froglabs API clients."""

import contextlib
import os

from tqdm.auto import tqdm
import pandas as pd
import requests
import six

from froglabs import exceptions


__copyright__ = 'Copyright 2019 Froglabs, Inc.'
__all__ = ['WeatherClient', 'TrainingClient']


if six.PY2:
    FileNotFoundError = IOError


@contextlib.contextmanager
def safe_open(path_or_obj, mode):
    if isinstance(path_or_obj, six.string_types):
        with open(path_or_obj, mode) as fh:
            yield fh
    else:
        yield path_or_obj


class Client(object):

    def __init__(self, host, scheme='http', token=None):
        self._host = host
        self._token = token
        self._api_url = '{}://{}'.format(scheme, host)
        self._session = requests.session()
        # We only want JSON back.
        self._session.headers.update({
            'Accept': 'application/json'
        })
        if token is not None:
            self._session.headers.update({
                'Authorization': 'Token {}'.format(token)
            })

    def _build_url(self, *path):
        return '/'.join([self._api_url] + list(map(str, path))) + '/'

    def request(self, method, path, params=None, data=None, json=None,
                files=None):
        """
        Makes an API request.

        Argument:
            method: str
                The HTTP method name (e.g. 'GET', 'POST', etc.)
            path: str, tuple
                A tuple of path tokens or full URL string. A tuple will be
                translated to a URL as follows: path[0]/path[1]/...
        """
        url = (self._build_url(*path)
               if not isinstance(path, six.string_types) else
               self._build_url(path))
        response = self._session.request(
            method,
            url,
            params=params,
            data=data,
            json=json,
            files=files
        )
        self.validate_response(response)
        return response

    @classmethod
    def validate_response(cls, response):
        if response.status_code >= 400:
            raise exceptions.HttpError(response)
        else:
            response.raise_for_status()


class WeatherClient(Client):
    """Froglabs Weather client."""

    def __init__(self, host=None, scheme='http'):
        super(WeatherClient, self).__init__(host or 'api.froglabs.ai', scheme)

    def query(self, output, location, variables, start_time, end_time,
              progress_bar=False):
        """Get and write weather to the output file.

        Arguments:
            output: str, object
                Path or file-like object.
            location: str, list or coordinates
            variables: list of strings
            start_time: datetime
            end_time: datetime
            progress_bar: bool
                Whether to enable progress bar.
        """
        if start_time >= end_time:
            raise ValueError('start_time >= end_time: %r >= %r' %
                             (start_time, end_time))
        url = self._build_url('weather')
        if not isinstance(location, six.string_types):
            if len(location) not in (2, 4):
                raise ValueError('Invalid location shape: %d' % len(location))
            location = ','.join(map(str, location))
        query = {
            'location': location,
            'variables': ','.join(variables),
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat()
        }

        chunk_size = 8 * 1024
        if progress_bar:
            def progress(response):
                desc = output if isinstance(output, six.string_types) else None
                size = int(response.headers['content-length'])
                return tqdm(
                    response.iter_content(chunk_size=chunk_size),
                    total=(size / chunk_size),
                    desc=desc,
                    unit='KB'
                )
        else:
            def progress(response):
                return response.iter_content(chunk_size=chunk_size)

        with self._session.post(url, json=query, stream=True) as response:
            self.validate_response(response)
            with safe_open(output, 'wb') as fh:
                for chunk in progress(response):
                    if chunk:
                        fh.write(chunk)

    def get_variables(self):
        response = self.request('GET', 'variables')
        return pd.read_json(response.text)


class TrainingClient(Client):
    """Froglabs Training client."""

    def __init__(self, host=None, scheme='http', token=None):
        super(TrainingClient, self).__init__(
            host or 'training.froglabs.ai',
            scheme,
            token
        )

    def get_variables(self):
        """Get supported weather variables."""
        response = self.request('GET', 'variables')
        return pd.read_json(response.json())

    def create_dataset(self, location, variables, path_or_obj):
        """Create training dataset.

        Arguments:
            location str, list
                Location name or coordinates.
            variables: list
                List of variable names
            path_or_obj: str, obj
                Path to time series data file
        """
        if isinstance(path_or_obj, six.string_types):
            if not os.path.exists(path_or_obj):
                raise FileNotFoundError(path_or_obj)
        if not isinstance(location, six.string_types):
            location = ','.join(map(str, location))

        with safe_open(path_or_obj, 'rb') as fh:
            response = self.request(
                'POST',
                'datasets',
                data={
                    'variables': ','.join(variables),
                    'location': location
                },
                files={'file': fh}
            )
        return response.json()

    def create_training_task(self, model, dataset, num_epochs=128,
                             batch_size=16,
                             window_size=None, seed=None, num_workers=0):
        """Creates training task for the given model and dataset.

        Arguments:
            model: str
                A model name (e.g. pvnet).
            dataset: int
                A dataset identifier.
        """
        response = self.request(
            'POST',
            'training_tasks',
            json={
                'model': model,
                'dataset': dataset,
                'num_epochs': num_epochs,
                'batch_size': batch_size,
                'window_size': window_size,
                'seed': seed,
                'num_workers': num_workers,
            }
        )
        return response.json()

    def get_training_task(self, task_id):
        response = self.request('GET', ('training_tasks', task_id))
        return response.json()
