import hashlib
import os
import random
import string
import subprocess
import sys
from pathlib import Path

import click
import jwt
import requests
import stups_cli
import stups_cli.config
import zign.api
from clickclick import Action, AliasedGroup

from . import APP_NAME, KUBECTL_VERSION, KUBECTL_SHA256, STERN_VERSION, STERN_SHA256


def auth_token():
    return zign.api.get_token('kubectl', ['uid'])


def _token_username():
    decoded_token = jwt.decode(auth_token(), verify=False)
    if decoded_token.get("https://identity.zalando.com/realm") == "users":
        return decoded_token.get("https://identity.zalando.com/managed-id")


def current_user():
    return zign.api.get_config().get('user') or _token_username()


def auth_headers():
    return {'Authorization': 'Bearer {}'.format(auth_token())}


def get_api_server_url(config):
    try:
        return config['api_server']
    except Exception:
        raise Exception("Unable to determine API server URL, please run zkubectl login")


class ExternalBinary:
    def __init__(self, env, name, url_template, version, sha256):
        self.env = env
        self.name = name
        self.url_template = url_template
        self.version = version
        self.sha256 = sha256

    def download(self):
        path = Path(os.getenv('KUBECTL_DOWNLOAD_DIR') or click.get_app_dir(APP_NAME))
        binary = path / '{}-{}'.format(self.name, self.version)

        if not binary.exists():
            try:
                binary.parent.mkdir(parents=True)
            except FileExistsError:
                # support Python 3.4
                # "exist_ok" was introduced with 3.5
                pass

            platform = sys.platform  # linux or darwin
            arch = 'amd64'  # FIXME: hardcoded value
            url = self.url_template.format(version=self.version, os=platform, arch=arch)
            with Action('Downloading {} to {}..'.format(url, binary)) as act:
                response = requests.get(url, stream=True)
                response.raise_for_status()
                # add random suffix to allow multiple downloads in parallel
                random_suffix = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
                local_file = binary.with_name('{}.download-{}'.format(binary.name, random_suffix))
                m = hashlib.sha256()
                with local_file.open('wb') as fd:
                    for i, chunk in enumerate(response.iter_content(chunk_size=4096)):
                        if chunk:  # filter out keep-alive new chunks
                            fd.write(chunk)
                            m.update(chunk)
                            if i % 256 == 0:  # every 1MB
                                act.progress()
                if m.hexdigest() != self.sha256[platform]:
                    act.fatal_error('CHECKSUM MISMATCH')
                local_file.chmod(0o755)
                local_file.rename(binary)

        return str(binary)

    def cmdline(self, *args):
        prefix = [self.download()]
        if self.env.namespace:
            prefix += ["-n", self.env.namespace]
        if self.env.kube_context:
            prefix += ["--context", self.env.kube_context]
        return prefix + list(args)

    def exec(self, *args):
        cmdline = self.cmdline(*args)
        sys.exit(subprocess.call(cmdline))


class Environment:
    def __init__(self):
        self.namespace = None
        self.kube_context = None
        self.config = stups_cli.config.load_config(APP_NAME)

        kubectl_template = 'https://storage.googleapis.com/kubernetes-release/release/{version}/bin/{os}/{arch}/kubectl'
        self.kubectl = ExternalBinary(self, 'kubectl',
                                      kubectl_template,
                                      KUBECTL_VERSION, KUBECTL_SHA256)
        self.stern = ExternalBinary(self, 'stern',
                                    'https://github.com/wercker/stern/releases/download/{version}/stern_{os}_{arch}',
                                    STERN_VERSION,
                                    STERN_SHA256)

    def store_config(self):
        stups_cli.config.store_config(self.config, APP_NAME)

    def set_namespace(self, namespace):
        self.namespace = namespace

    def set_kube_context(self, kube_context):
        self.kube_context = kube_context


class DecoratingGroup(AliasedGroup):
    """An AliasedGroup that decorates all commands added to the group with a given decorator. If the command is also
       a DecoratingGroup, the decorator is propagated as well."""

    def __init__(self, name=None, commands=None, **attrs):
        super(DecoratingGroup, self).__init__(name=name, commands=commands, **attrs)
        self.decorator = None

    def add_command(self, cmd, name=None):
        if self.decorator:
            cmd = self.decorator(cmd)
        if isinstance(cmd, DecoratingGroup):
            cmd.decorator = self.decorator
        super(DecoratingGroup, self).add_command(cmd, name=name)
