# coding=utf-8

from tweb import base_handler, myweb
from tweb.error_exception import ErrException, ERROR
from tornado import gen
import json
from ..service.async_wrap import ctrl_contract
from webmother.utils import user_auth


class QueryContractsHandler(base_handler.BaseHandler):
    @gen.coroutine
    def get(self, cid, **kwargs):
        uid = self.request.headers.get('x-user-id')
        access_token = self.request.headers.get('x-access-token')
        passport = self.request.headers.get('x-signed-passport')

        page_no = int(self.get_argument('page_no', 1))
        page_size = int(self.get_argument('page_size', 10))

        auth = yield user_auth.verify(uid, access_token, self.request.remote_ip)

        array, total = yield ctrl_contract.query_contracts(cid, page_no, page_size, passport, auth[1])
        return self.write({
            'total': total,
            'list': array
        })


class ContractHandler(base_handler.BaseHandler):
    """
    注册/注销合约
    """

    @myweb.authenticated
    @gen.coroutine
    def post(self, cid, contract_id, **kwargs):
        passport = self.request.headers.get('x-signed-passport')
        access_token = self.request.headers.get('x-access-token')

        data = json.loads(self.request.body.decode('utf-8'))
        if 'name' not in data:
            raise ErrException(ERROR.E40000, extra='not name field')
        if 'symbol' not in data:
            raise ErrException(ERROR.E40000, extra='not symbol field')
        if 'decimals' not in data:
            raise ErrException(ERROR.E40000, extra='not decimals field')
        if 'type' not in data:
            raise ErrException(ERROR.E40000, extra='not type field, value like: main, ERC20')

        ret = yield ctrl_contract.register(cid, data, passport, access_token)
        return self.write(ret)

    @myweb.authenticated
    @gen.coroutine
    def delete(self, cid, contract_id, **kwargs):
        passport = self.request.headers.get('x-signed-passport')
        access_token = self.request.headers.get('x-access-token')

        ret = yield ctrl_contract.unregister(cid, contract_id, passport, access_token)
        return self.write(ret)

    @gen.coroutine
    def get(self, cid, contract_id, **kwargs):
        uid = self.request.headers.get('x-user-id')
        access_token = self.request.headers.get('x-access-token')
        passport = self.request.headers.get('x-signed-passport')

        auth = yield user_auth.verify(uid, access_token, self.request.remote_ip)

        ret = yield ctrl_contract.read(cid, contract_id, passport, auth[1])
        return self.write(ret)
