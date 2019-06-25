import os
import json
import requests
import keyring

from datetime import datetime
from logging import getLogger
from getpass import getuser
from filelock import FileLock
from collabi.open_struct import OpenStruct

class CloudConfig(OpenStruct):
    def __init__(self, env):
        self.env = env
        self._user = getuser()
        self._logger = getLogger(CloudConfig._NAME)
        self._rcfn = self._expand_rcfn(self.env)
        self._lock = FileLock(self._rcfn + '.lock')

        if isinstance(keyring.get_keyring(), keyring.backends.fail.Keyring):
            self._keyring_service = None
            self._secret_keys = []
        else:
            self._keyring_service = CloudConfig._NAME + '.' + self.env
            self._secret_keys = ['access_token', 'refresh_token']

        cfg = {}
        if os.path.exists(self._rcfn):
            with self._lock.acquire(timeout=CloudConfig._LOCK_TIMEOUT):
                with open(self._rcfn) as rcf:
                    cfg = json.load(rcf)
                    if 'expiry' in cfg:
                        cfg['expiry'] = self._decode_expiry(cfg['expiry'])
            self._logger.debug('Read config from '+self._rcfn)
        super(CloudConfig, self).__init__(cfg)
        self._load_secrets()

    def update(self):
        url = 'https://public-cdn.cloud.unity3d.com/config/'+self.env
        resp = requests.get(url)
        resp.raise_for_status()
        cfg = resp.json()
        self._logger.debug('Read config from '+url)
        super(CloudConfig, self).update_with(cfg)

    def save(self, **kwargs):
        self._save_secrets()
        if 'delete' in kwargs:
            to_delete = kwargs['delete']
            del(kwargs['delete'])
        else:
            to_delete = []
        for key, val in self.__dict__.iteritems():
            if key[0] == '_' or key in to_delete or key in self._secret_keys:
                continue
            if key == 'expiry':
                kwargs[key] = self._encode_expiry(val)
            elif key not in kwargs:
                kwargs[key] = val
        with self._lock.acquire(timeout=CloudConfig._LOCK_TIMEOUT):
            with open(self._rcfn, 'wb') as rcf:
                json.dump(kwargs, rcf)
        os.chmod(self._rcfn, 0600) # since it houses sensitive tokens (see TODO above)
        self._logger.debug('Saved config to '+self._rcfn)

    ########################################
    # private

    _NAME = 'unity.collab.cloud_config'
    _LOCK_TIMEOUT = 10
    _EXPIRY_FORMAT = '%Y-%m-%d %H:%M:%S '

    def _load_secrets(self):
        if not self._keyring_service: return
        for key in self._secret_keys:
            val = keyring.get_password(self._keyring_service, self._user + '.' + key)
            if val: self[key] = val

    # TODO: save everything in one key (with two, it prompts twice to allow, which is annoying)
    def _save_secrets(self):
        if not self._keyring_service:
            if not self.secrets_warning_issued:
                self.secrets_warning_issued = True
                self._logger.warn('No keyring available: storing secrets directly in config')
            return
        for key in self._secret_keys:
            val = self[key]
            if val: keyring.set_password(self._keyring_service, self._user + '.' + key, val)

    @staticmethod
    def _expand_rcfn(env):
        return os.path.join(os.path.expanduser('~'), '.cloud'+env+'rc')

    @staticmethod
    def _decode_expiry(s):
        return datetime.strptime(s, CloudConfig._EXPIRY_FORMAT+'%Z')

    @staticmethod
    def _encode_expiry(e):
        return e.strftime(CloudConfig._EXPIRY_FORMAT+'UTC')
