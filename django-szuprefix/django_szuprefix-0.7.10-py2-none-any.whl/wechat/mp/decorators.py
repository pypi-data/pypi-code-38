# -*- coding:utf-8 -*- 
from functools import wraps

from django.http import HttpResponseRedirect
from django.utils.decorators import available_attrs
from .helper import api
from django.contrib import auth


def user_passes_test(test_func):
    u"""
      重写user_passes_test是因为django.contrib.auth.decorators.user_passes_test里面的redirect_to_login会把url参数
      的顺序给打乱，但微信的安全检验又是限定了参数顺序的，不兼容。
      同时也是因为从外部登录完回来时，要处理一下django的登录事宜。
    """

    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            state = request.GET.get("state")
            if "WEIXIN_LOGIN" == state:
                code = request.GET.get("code")
                user = auth.authenticate(code=code)
                auth.login(request, user)
                return view_func(request, *args, **kwargs)
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            login_url = api.OAuthUrl(request.build_absolute_uri())
            return HttpResponseRedirect(login_url)

        return _wrapped_view

    return decorator


def weixin_login_required(function=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated(),
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
