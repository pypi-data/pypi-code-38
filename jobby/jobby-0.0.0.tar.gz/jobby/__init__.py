import datetime as _dt
import os as _os

from envbash import load_envbash as _load_envbash
from pymongo import MongoClient as _MongoClient

from jobby.utils import get_env as _get_env


class JobbyJob(object):
    def __init__(self, args, namespace='job'):
        assert type(args) is dict

        _load_envbash(_os.path.join(
            _os.getcwd(), '.jobby', '.env'))

        self._db_url = '%s:27017' % _get_env('JOBBY_NETWORK_HOST')
        self._db_name = _get_env('JOBBY_PROJECT_NAME')
        self._namespace = namespace
        self._args = args
        self._out = dict()
        self._started = None
        self._ended = None

    def __enter__(self):
        self._started = _dt.datetime.now()
        return self

    def __exit__(self, *args):
        self._ended = _dt.datetime.now()

        doc = {
            'started': self._started,
            'ended': self._ended,
            'args': self._args,
            'out': self._out
        }

        try:
            with _MongoClient(self._db_url) as db_client:
                db = db_client[self._db_name]
                collection = db[self._namespace]
                collection.insert_one(doc)
        
        except Exception as e:
            print(e)

    def update_output(self, **kwargs):
        self._out.update(kwargs)
