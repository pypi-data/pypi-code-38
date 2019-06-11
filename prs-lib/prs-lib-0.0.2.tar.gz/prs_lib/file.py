import prs_utility as utility

from .request import request
from . import sign_utility
from . import validator

__all__ = ['File', ]


class File:
    def __init__(self, config):
        """
        :param config: PRSConfig
        """
        self.config = config

    @staticmethod
    def omit_sign_data(data):
        omit_keys = [
            'address', 'signature', 'fileHash', 'title', 'source', 'originUrl',
            'category', 'projectId',
        ]
        omit_data = dict()
        for k, v in data.items():
            if k not in omit_keys:
                omit_data[k] = v
        return omit_data

    def sign_by_file_reader(self, data, meta=None):
        """
        :param data: dict
            {
                'file': 'file reader',
                'filename': str,
                'title': str,
                'source': str,
                'origin_url': str,
                'category': str,
                'project_id': int,
            }
        :param meta: object
        """
        required = ['file', 'filename', 'title']
        validator.check_dict_and_assert('data', data, required)
        meta = self.omit_sign_data(meta or dict())
        auth_opts = self.config.get_auth_opts()
        private_key, token = auth_opts['private_key'], auth_opts['token']
        file_hash = sign_utility.hash_by_file_reader(data['file'])
        block_data = {'file_hash': file_hash}
        sign = None
        if private_key:
            sign = utility.sign_block_data(block_data, private_key)
        elif token:
            res = sign_utility.sign_by_token(
                block_data, token, self.config.host
            )
            sign = res.json()

        address = utility.sig_to_address(sign['hash'], sign['signature'])
        fields = {
            'address': address,
            'signature': sign['signature'],
            'title': data['title']
        }
        if data.get('source'):
            fields['source'] = data['source']
        if data.get('origin_url'):
            fields['originUrl'] = data['origin_url']
        if data.get('category'):
            fields['category'] = data['category']
        if data.get('project_id'):
            fields['projectId'] = data['project_id']
        fields.update(meta)

        file_data = {
            'field': 'file',
            'file': data['file'],
            'filename': data['filename'],
        }
        return request(
            self.config.host,
            method='POST',
            path='/files',
            fields=fields,
            file_data=file_data,
            debug=self.config.debug,
        )

    def sign_by_stream(self, data, meta=None):
        """
        :param data: dict
            {
                'stream': 'file stream',
                'filename': str,
                'title': str,
                'source': str,
                'origin_url': str,
                'category': str,
                'project_id': int,
            }
        :param meta: object
        """
        required = ['stream', 'filename', 'title']
        validator.check_dict_and_assert('data', data, required)
        meta = self.omit_sign_data(meta or dict())
        auth_opts = self.config.get_auth_opts()
        private_key, token = auth_opts['private_key'], auth_opts['token']
        buffer, file_hash = sign_utility.hash_by_readable_stream(
            data['stream']
        )
        block_data = {'file_hash': file_hash}
        sign = None
        if private_key:
            sign = utility.sign_block_data(block_data, private_key)
        elif token:
            res = sign_utility.sign_by_token(
                block_data, token, self.config.host
            )
            sign = res.json()

        address = utility.sig_to_address(sign['hash'], sign['signature'])
        fields = {
            'address': address,
            'signature': sign['signature'],
            'title': data['title']
        }
        if data.get('source'):
            fields['source'] = data['source']
        if data.get('origin_url'):
            fields['originUrl'] = data['origin_url']
        if data.get('category'):
            fields['category'] = data['category']
        if data.get('project_id'):
            fields['projectId'] = data['project_id']
        fields.update(meta)

        file_data = {
            'field': 'file',
            'file': buffer,
            'filename': data['filename'],
        }
        return request(
            self.config.host,
            method='POST',
            path='/files',
            fields=fields,
            file_data=file_data,
            debug=self.config.debug,
        )

    def sign_by_buffer(self, data, meta=None):
        """
        :param data: dict
            {
                'buffer': 'file buffer',
                'filename': str,
                'title': str,
                'source': str,
                'origin_url': str,
                'category': str,
                'project_id': int,
            }
        :param meta: object
        """
        required = ['buffer', 'filename', 'title']
        validator.check_dict_and_assert('data', data, required)
        meta = self.omit_sign_data(meta or dict())
        auth_opts = self.config.get_auth_opts()
        private_key, token = auth_opts['private_key'], auth_opts['token']
        file_hash = utility.keccak256(data['buffer'])
        block_data = {'file_hash': file_hash}
        sign = None
        if private_key:
            sign = utility.sign_block_data(block_data, private_key)
        elif token:
            res = sign_utility.sign_by_token(
                block_data, token, self.config.host
            )
            sign = res.json()

        address = utility.sig_to_address(sign['hash'], sign['signature'])
        fields = {
            'address': address,
            'signature': sign['signature'],
            'title': data['title']
        }
        if data.get('source'):
            fields['source'] = data['source']
        if data.get('origin_url'):
            fields['originUrl'] = data['origin_url']
        if data.get('category'):
            fields['category'] = data['category']
        if data.get('project_id'):
            fields['projectId'] = data['project_id']
        fields.update(meta)

        file_data = {
            'field': 'file',
            'file': data['buffer'],
            'filename': data['filename'],
        }
        return request(
            self.config.host,
            method='POST',
            path='/files',
            fields=fields,
            file_data=file_data,
            debug=self.config.debug,
        )

    def get_by_rid(self, rid):
        """
        :param rid: str
        """
        validator.assert_exc(rid, 'rid cannot be null')
        return request(
            self.config.host,
            method='GET',
            path=f'/files/{rid}',
            auth_opts=self.config.get_auth_opts(),
            debug=self.config.debug
        )

    def get_by_msghash(self, msghash):
        """
        :param msghash: str
        """
        validator.assert_exc(msghash, 'msghash cannot be null')
        return request(
            self.config.host,
            method='GET',
            path=f'/files/hash/{msghash}',
            auth_opts=self.config.get_auth_opts(),
            debug=self.config.debug
        )

    def reward(self, rid, amount, comment=None):
        """
        :param rid: str
        :param amount: int
        :param comment: str
        """
        validator.assert_exc(rid, 'rid cannot be null')
        validator.assert_exc(amount, 'amount cannot be null')
        data = {'amount': amount}
        if comment:
            data['comment'] = comment
        return request(
            self.config.host,
            method='POST',
            path=f'/files/{rid}/reward',
            data=data,
            auth_opts=self.config.get_auth_opts(),
            debug=self.config.debug
        )

    def get_feeds(self, address, offset=0, limit=10):
        """
        :param address: str
        :param offset: int
        :param limit: int
        """
        validator.assert_exc(address, 'address cannot be null')
        query = {'offset': offset, 'limit': limit}
        return request(
            self.config.host,
            method='GET',
            path=f'/users/{address}/feed.json',
            query=query,
            debug=self.config.debug
        )
