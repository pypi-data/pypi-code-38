# -*- coding: utf-8 -*-

from binascii import b2a_hex, a2b_hex

from Crypto.Cipher import AES

from rest_framework import status

from django.http import Http404, HttpResponseRedirect

from bigtiger.utils.unique import get_uuid
from bigtiger.utils.encryp import HexAES

from django_restful import RestfulApiView, RestfulApiError, DoesNotExistError, view_http_method
from django_restful.response import ErrorResponse, Response
from django_restful.utils.url import build_url

from bigtiger.contrib.admin.models.microapp_app import MicroappAppModel
from bigtiger.contrib.admin.models.microapp_token import MicroappTokenModel

from django_sae.models.session import SessionModel


def _aes_encrypt(app_secret, session_key):
    """session_key加密"""

    aes = HexAES(app_secret, AES.MODE_ECB)
    return aes.encrypt(session_key)


class MicroAppTokenList(RestfulApiView):

    @view_http_method('get')
    def connect(self, request):
        """ 用于微应用框架session共享，返回session或会话临时票据, 通过重定向到app_id对应的sso_url.

        调用示例：
        http://127.0.0.1:8000/api/sso/connect/?appid=123&response_type=session&redirect_uri=http://www.baidu.com
        http://127.0.0.1:8000/api/sso/connect/?appid=123&response_type=code&redirect_uri=http://www.baidu.com
        """

        query = request.GET.copy()

        session_key = request.session.session_key
        if session_key is None:
            raise Http404()

        session_service = SessionModel()
        session = session_service.get_one(session_key)
        if session is None:
            return ErrorResponse('session id does not exist.')

        app_code = query.get('appid', None)
        response_type = query.get('response_type', 'session')
        redirect_uri = query.get('redirect_uri', None)
        state = query.get('state', '')

        if redirect_uri is None:
            return ErrorResponse('redirect_uri is null.')
        if app_code is None:
            return ErrorResponse('appid is null.')

        app_service = MicroappAppModel()
        app = app_service.get_one_app_code(app_code)
        if app is None:
            return ErrorResponse('app does not exist.')
        if app['status'] == 0:
            return ErrorResponse('app disable.')
        app_secret = app['app_secret']
        sso_url = app['sso_url']

        if response_type == 'session':
            url = build_url(sso_url, extra_params={
                'redirect_uri': redirect_uri, 'session_id': _aes_encrypt(app_secret, session_key), 'state': state})
            return HttpResponseRedirect(url)
        elif response_type == 'code':
            token_code = get_uuid()
            entity = {
                'id': get_uuid(),
                'app_id': app['id'],
                'app_secret': app_secret,
                'token_code': token_code,
                'grant_type': 'authorization_code',
                'session_id': session_key,
                'expire_date': request.session.get_expiry_date()
            }

            service = MicroappTokenModel()
            service.add(entity)

            url = build_url(sso_url, extra_params={
                'redirect_uri': redirect_uri, 'code': token_code, 'state': state})
            return HttpResponseRedirect(url)
        else:
            return ErrorResponse('response_type value error.')

    @view_http_method('get')
    def access_token(self, request):
        """ 通过临时会话票据获取session id.

        http://127.0.0.1:8000/api/sso/access_token/?appid=123&token_code=794277f1-1f44-4dd2-95e7-90b3d7e97029&redirect_uri=http://www.baidu.com
        """

        try:
            query = request.GET.copy()

            app_code = query.get('appid', None)
            token_code = query.get('token_code', None)
            grant_type = query.get('grant_type', 'authorization_code')

            service = MicroappAppModel()
            app = service.get_one_app_code(app_code)
            if app is None:
                return ErrorResponse('app does not exist.')
            if app['status'] == 0:
                return ErrorResponse('app disable.')

            service = MicroappTokenModel()
            lst = service.get_list_token_code(app['id'], token_code)

            if lst:
                token = lst.pop()
                return Response({'session_id': _aes_encrypt(app['app_secret'], token['session_id']), 'expire_date': token['expire_date']})
            raise DoesNotExistError(u'未找到数据.')
        except DoesNotExistError as ex:
            return ErrorResponse(ex)
