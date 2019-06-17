# coding=utf-8

from tweb import base_handler, myweb
from tornado import gen
from webmother.service.async_wrap import ctrl_entrance
from ..extra_passport import system_name


class EmployPassportsHandler(base_handler.BaseHandler):
    """
    获取我们(组织)的授权列表
    """

    @myweb.authenticated
    @gen.coroutine
    def get(self,  **kwargs):
        employment = self.request.headers.get('x-signed-employment')
        access_token = self.request.headers.get('x-access-token')

        array, display = yield ctrl_entrance.employ_passports(system_name, employment, access_token)

        return self.write({'list': array, 'passport_display': display})
