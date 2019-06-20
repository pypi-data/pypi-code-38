from typing import *
from fifteenrock.core import core
from fifteenrock.core import fr_notebook
from fifteenrock.lib import helper


class ComputeClient(object):
    def __init__(self, url: str, credentials: Dict, credentials_file: str):
        self.url = url
        self.credentials = credentials
        self.credentials_file = credentials_file
        pass

    def deploy(self, *args, **kwargs):
        new_kwargs = {**kwargs,
                      **self._common_args()}
        return core.deploy(*args, **new_kwargs)

    def deploy_notebook(self, *args, **kwargs):
        new_kwargs = {**kwargs,
                      **self._common_args()}
        return fr_notebook.deploy_notebook(*args, **new_kwargs)

    def delete_function(self, *args, **kwargs):
        new_kwargs = {**kwargs,
                      **self._common_args()}
        return core.delete_function(*args, **new_kwargs)

    def list_functions(self, *args, **kwargs):
        new_kwargs = {**kwargs,
                      **self._common_args()}
        return core.list_functions(*args, **new_kwargs)

    def logs(self, *args, **kwargs):
        new_kwargs = {**kwargs,
                      **self._common_args()}
        return core.logs(*args, **new_kwargs)

    def _common_args(self):
        return dict(url=self.url, credentials=self.credentials, credentials_file=self.credentials_file)


def compute(url: str = "https://app.15rock.com/gateway/compute", credentials: Dict = None,
            credentials_file: str = None) -> ComputeClient:
    """

    :param url:
    :param credentials:
    :param credentials_file: Currently, this cannot be provided explicitly when called in a notebook setting. The file
    has to be stored as fifteenrock.json in the root of the home folder of the notebook.
    :return:
    """
    # credentials = credentials or helper.get_credentials(credentials, credentials_file)
    return ComputeClient(url, credentials, credentials_file)
