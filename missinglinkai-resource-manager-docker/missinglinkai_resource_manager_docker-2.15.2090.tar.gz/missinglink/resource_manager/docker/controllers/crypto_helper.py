import msgpack
import requests
from missinglink.crypto import Envelope, Asymmetric, MultiKeyEnvelope
from missinglink.crypto.cipher import Cipher


class DecryptionError(Exception):
    pass


class MlCryptionCipher(Cipher):
    def __init__(self, active_config, org, invocation_id, decryption_token):
        self.invocation_id = invocation_id
        self.decryption_token = decryption_token
        self.active_config = active_config
        self.org = org
        self.backend_base_url = active_config.general.get('backend_base_url', 'https://missinglinkai.appspot.com/_ah/api/missinglink/v1')

    def decrypt(self, data):
        url = f'{self.backend_base_url}/{self.org}/run/decrypt_with_token/{self.invocation_id}'
        data = {
            'decryption_token': self.decryption_token,
            'invocation_id': self.invocation_id,
            'rm_server': self.active_config.general.cluster_id,
            'key': self.bytes_to_b64str(data)
        }
        response = requests.post(url=url, json=data, verify=True)

        if response.status_code != 200:
            raise DecryptionError('Failed to decrypt key against %s, response was: %s', url, response.text)
        return self.b64str_to_bytes(response.json()['key'])

    def encrypt(self, data):
        raise NotImplementedError('%s only supports decryption', self.__class__)


class MlCrytionEnvelopeCipher(Envelope):
    def __init__(self, *args, **kwargs):
        super(MlCrytionEnvelopeCipher, self).__init__(MlCryptionCipher.create_from(*args, **kwargs))


class CryptoHelper:
    def __init__(self, active_config):
        self.active_config = active_config

    def default_cipher(self):
        return Asymmetric.create_from(
            Asymmetric.b64str_to_bytes(self.active_config.general.default_private_key)
        )

    def decrypt_cloud_native(self, data):
        return MultiKeyEnvelope(self.default_cipher()).decrypt(data)

    def decrypt_invocation(self, invocation):
        protocol_version = invocation.encrypted.get('version', 1)
        if protocol_version == 1:
            cipher = MlCrytionEnvelopeCipher.create_from(
                self.active_config, invocation.org, invocation.invocation_id, invocation.encrypted.get('token')
            )
            data = cipher.decrypt(cipher.b64str_to_bytes(invocation.encrypted.get('data')))

            res = msgpack.unpackb(self.decrypt_cloud_native(data))
            return res[b'data']

        raise NotImplementedError('Encryption version %s is not supported' % protocol_version)
