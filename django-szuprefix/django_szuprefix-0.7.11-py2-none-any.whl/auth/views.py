# -*- coding:utf-8 -*-
from django.http import JsonResponse
from django.views.generic import FormView, View
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm

from django_szuprefix.utils import datautils
from django_szuprefix.utils.views import FormResponseJsonMixin, ContextJsonDumpsMixin


def get_user_json(user):
    if user.is_authenticated():
        user = {"name": user.get_full_name(),
                "id": user.pk,
                'permissions': list(user.get_all_permissions()),
                'groups': list(user.groups.values_list('name', flat=True))
                }
    else:
        user = {}
    return user

class LoginView(FormResponseJsonMixin, ContextJsonDumpsMixin, FormView):
    form_class = AuthenticationForm

    def form_valid(self, form):
        from django.contrib.auth import login as auth_login
        user = form.get_user()
        auth_login(self.request, user)
        return JsonResponse(dict(code=0, msg='ok', data=get_user_json(user)), encoder=datautils.JSONEncoder)


class LogoutView(View):
    def post(self, request):
        from django.contrib.auth import logout
        logout(request)
        return JsonResponse(dict(code=0, msg='ok'))


class PasswordChangeView(FormResponseJsonMixin, ContextJsonDumpsMixin, FormView):
    form_class = PasswordChangeForm

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(self.request.user, **self.get_form_kwargs())


class GetUserInfoView(View):
    def get(self, request):
        from django.middleware.csrf import get_token
        get_token(request)
        user = request.user

        return JsonResponse(get_user_json(user))
