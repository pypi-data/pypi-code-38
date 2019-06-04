from typing import *
from fifteenrock.core import core
from fifteenrock.core import fr_notebook
from fifteenrock.lib import helper


class ComputeClient(object):
    def __init__(self, url: str, credentials: Dict):
        # self._url = url + "/api/v0/db"
        self.url = url
        self.credentials = credentials
        pass

    def deploy(self, *args, **kwargs):
        new_kwargs = {**kwargs, **dict(url=self.url, credentials=self.credentials)}
        return core.deploy(*args, **new_kwargs)

    def deploy_notebook(self, *args, **kwargs):
        new_kwargs = {**kwargs, **dict(url=self.url, credentials=self.credentials)}
        return fr_notebook.deploy_notebook(*args, **new_kwargs)


def compute(url: str = "https://app.15rock.com/gateway/compute", credentials: Dict = None,
            credentials_file: str = None) -> ComputeClient:
    credentials = credentials or helper.get_credentials(credentials, credentials_file)
    return ComputeClient(url, credentials)
