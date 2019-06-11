from .request import request
from . import validator

__all__ = ['Order', ]


class Order:
    def __init__(self, config):
        """
        :param config: PRSConfig
        """
        self.config = config

    def create(self, contract_rid, file_rid, license_type):
        """
        :param contract_rid: str
        :param file_rid: str
        :param license_type: str
        """
        validator.assert_exc(contract_rid, 'contract_rid cannot be null')
        validator.assert_exc(file_rid, 'file_rid cannot be null')
        validator.assert_exc(license_type, 'license_type cannot be null')
        data = {
            'contractRId': contract_rid,
            'fileRId': file_rid,
            'licenseType': license_type,
        }
        return request(
            self.config.host,
            method='POST',
            path='/orders',
            data=data,
            auth_opts=self.config.get_auth_opts(),
            debug=self.config.debug,
        )

    def get_orders_by_contract_rid(self, contract_rid, offset=0, limit=10):
        """
        :param contract_rid: str
        :param offset: int, default value: 0
        :param limit: int, default value: 10
        """
        validator.assert_exc(contract_rid, 'contract_rid cannot be null')
        query = {'offset': offset, 'limit': limit}
        return request(
            self.config.host,
            method='GET',
            path=f'/contracts/{contract_rid}/orders',
            query=query,
            auth_opts=self.config.get_auth_opts(),
            debug=self.config.debug,
        )

    def get_purchased_orders(self, offset=0, limit=10):
        """
        :param offset: int, default value: 0
        :param limit: int, default value: 10
        """
        query = {'offset': offset, 'limit': limit}
        return request(
            self.config.host,
            method='GET',
            path='/orders',
            query=query,
            auth_opts=self.config.get_auth_opts(),
            debug=self.config.debug,
        )

    def get_order_by_rid(self, rid):
        """
        :param rid: str
        """
        validator.assert_exc(rid, 'order rid cannot be null')
        return request(
            self.config.host,
            method='GET',
            path=f'/orders/{rid}',
            auth_opts=self.config.get_auth_opts(),
            debug=self.config.debug,
        )
