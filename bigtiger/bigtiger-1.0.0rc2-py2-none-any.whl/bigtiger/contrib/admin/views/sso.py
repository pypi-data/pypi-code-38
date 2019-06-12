# encoding: utf-8

from django.conf import settings
from django.http import HttpResponseForbidden
from django.views.generic import RedirectView

from bigtiger.core.exceptions import AuthenticateError
from bigtiger.utils.tree import tree_sorted
from bigtiger.contrib.admin.views.mainview import LoginView

from django_sae.models.user import UserModel

from bigtiger.contrib.admin.models.auth_permission import AuthPermissionModel



class SsoRefererView(RedirectView):
    permanent = False
    url = settings.SSO_REFERER_URL


class SsoLoginView(LoginView):
    """
    单点登陆,根据用户名实现
    url:sso/(?P<pk>.*)/login/ 其中的pk为sso_username。
    """

    def _get_sso_user(self, sso_token):
        # 根据单位和姓名判断用户用户的对应关系
        r = requests.get(SSO_USER_URL + sso_token)
        sso_user = json.loads(r.json())
        return sso_user

    def _get_sys_user(self, sso_user_name):
        user_model = UserModel()
        lst = user_model.get_all()
        if lst:
            users = filter(
                lambda item: item['login_name'] == sso_user_name, lst)
            if users:
                return users[0]
        return None

    def get(self, request, *args, **kwargs):
        # 判断sso的引荐页面是否正确
        referrer = request.META['HTTP_REFERER']
        if settings.SSO_REFERER_URL.find(referrer) == -1:
            return HttpResponseForbidden('你没有权限访问此网站。')

        # 根据sso_username获取本地的用户信息并自动登陆
        sso_username = self.kwargs['pk']
        sys_user = self._get_sys_user(sso_username)
        if sys_user is None:
            sys_user = self._get_sys_user('guest')

        if sys_user is None:
            return HttpResponseForbidden('你没有权限访问此网站。')
        else:
            user_name = sys_user['login_name']
            password = sys_user['login_password']
        try:
            return self.authenticate(user_name, password)
        except AuthenticateError as e:
            return HttpResponseForbidden('你没有权限访问此网站。')

