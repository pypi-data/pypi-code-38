from django.http import HttpRequest
from django.db.models import Model
from CTUtil.util import TokenSerializer
from CTUtil.Response.response import resp_error_json
from CTUtil.types import ResponseStates
from functools import wraps
from typing import Type
from traceback import print_exc
import time
from itsdangerous import SignatureExpired


def login_require(token_object: Type[TokenSerializer], valid_modle: Type[Model]):
    def _login_require(view_func):
        @wraps(view_func)
        def _do_someting(request: Type[HttpRequest]):
            token: str = request.META.setdefault('HTTP_TOKEN')
            if not token:
                return resp_error_json('请先登录系统', ResponseStates.LOGIN_ERROR)
            try:
                _id: int = int(token_object.decode(token.encode()).setdefault('user_id', 0))
                user = valid_modle.objects.filter(id=_id).first()
                if not user:
                    return resp_error_json('用户不存在')
                request.user = user
            except SignatureExpired as ex:
                return resp_error_json('用户已过期, 请重新登录', ResponseStates.LOGIN_ERROR)
            except Exception as ex:
                print_exc()
                return resp_error_json('系统错误')
            return view_func(request)
        return _do_someting
    return _login_require


def login_token(token_object: Type[TokenSerializer], valid_model: Type[Model]):
    data = {
        'user_id': valid_model.id,
        'username': valid_model.username,
        'timestamp': time.time(),
    }
    return token_object.encode(data).decode()