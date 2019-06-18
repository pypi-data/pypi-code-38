import os
from os.path import expanduser

from sidecar.const import Const


class KubTokenProvider:
    def get_token(self):
        with open(Const.get_kubernetes_token_file_path(), 'r') as pod_token_file:
            return pod_token_file.read().replace('\n', '')


class FakeKubTokenProvider(KubTokenProvider):
    def get_token(self):
        with open(os.path.join(expanduser("~"), 'sidecar/kub_token',), 'r') as token_file:
            return token_file.read().replace('\n', '')
