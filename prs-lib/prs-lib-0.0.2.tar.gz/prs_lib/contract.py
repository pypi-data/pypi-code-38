import prs_utility as utility

from .request import request
from . import validator
from . import sign_utility

__all__ = ['Contract', ]


class Contract:
    def __init__(self, config):
        """
        :param config: PRSConfig
        """
        self.config = config

    def get_templates(self, _type=None):
        """
        :param _type: str, e.g.: 'text' or 'image'
        """
        query = {'type': _type} if _type else None
        return request(
            self.config.host,
            method='GET',
            path='/contracts/templates',
            query=query,
            debug=self.config.debug,
        )

    def create(self, code):
        """
        :param code: str
        """
        validator.assert_exc(code, 'code cannot be null')
        code_hash = utility.keccak256(code)
        block_data = {'file_hash': code_hash}
        auth_opts = self.config.get_auth_opts()
        private_key = auth_opts.get('private_key')
        token = auth_opts.get('token')
        sign = None
        if private_key:
            sign = utility.sign_block_data(block_data, private_key)
        elif token:
            res = sign_utility.sign_by_token(
                block_data, token, self.config.host
            )
            sign = res.json()
        data = {
            'code': code,
            'signature': sign['signature'],
        }
        return request(
            self.config.host,
            method='POST',
            path='/contracts',
            data=data,
            auth_opts=self.config.get_auth_opts(),
            debug=self.config.debug,
        )

    def bind(self, contract_rid, file_rid, beneficiary_address):
        """
        :param contract_rid: str
        :param file_rid: str
        :param beneficiary_address: str
        """
        validator.assert_exc(contract_rid, 'contract_rid cannot be null')
        validator.assert_exc(file_rid, 'file_rid cannot be null')
        validator.assert_exc(
            beneficiary_address, 'beneficiary_address cannot be null'
        )
        block_data = {
            'beneficiary_address': beneficiary_address,
            'content_id': file_rid,
            'contract_id': contract_rid,
        }
        auth_opts = self.config.get_auth_opts()
        private_key = auth_opts.get('private_key')
        token = auth_opts.get('token')
        sign = None
        if private_key:
            sign = utility.sign_block_data(block_data, private_key)
        elif token:
            res = sign_utility.sign_by_token(
                block_data, token, self.config.host
            )
            sign = res.json()
        data = {
            'signature': sign['signature'],
            'fileRId': file_rid,
        }
        return request(
            self.config.host,
            method='POST',
            path=f'/contracts/{contract_rid}/bind',
            data=data,
            auth_opts=auth_opts,
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
            path=f'/contracts/{rid}',
            auth_opts=self.config.get_auth_opts(),
            debug=self.config.debug,
        )

    def get_contracts(self, offset=0, limit=10):
        """
        :param offset: int, default value: 0
        :param limit: int, default value: 10
        """
        query = {'offset': offset, 'limit': limit}
        return request(
            self.config.host,
            method='GET',
            path='/contracts',
            query=query,
            auth_opts=self.config.get_auth_opts(),
            debug=self.config.debug,
        )
