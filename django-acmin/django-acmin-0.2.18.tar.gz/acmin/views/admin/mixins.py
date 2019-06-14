from acmin.models import Permission, ContentType
from acmin.utils import attr


class AccessMixin:
    from django.contrib.auth import REDIRECT_FIELD_NAME
    login_url = None
    permission_denied_message = ''
    raise_exception = False
    redirect_field_name = REDIRECT_FIELD_NAME

    def get_login_url(self):
        from django.core.exceptions import ImproperlyConfigured
        from django.conf import settings
        login_url = self.login_url or settings.LOGIN_URL
        if not login_url:
            raise ImproperlyConfigured(
                '{0} is missing the login_url attribute. Define {0}.login_url, settings.LOGIN_URL, or override '
                '{0}.get_login_url().'.format(self.__class__.__name__)
            )
        return str(login_url)

    def get_permission_denied_message(self):
        return self.permission_denied_message

    def get_redirect_field_name(self):
        return self.redirect_field_name

    def handle_no_permission(self):
        from django.contrib.auth.views import redirect_to_login
        from django.core.exceptions import PermissionDenied
        if self.raise_exception or self.request.user.is_authenticated:
            raise PermissionDenied(self.get_permission_denied_message())
        return redirect_to_login(self.request.get_full_path(), self.get_login_url(), self.get_redirect_field_name())

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and self.has_permission():
            return super().dispatch(request, *args, **kwargs)
        else:
            return self.handle_no_permission()

    def has_permission(self):
        return True


class ContextMixin(object):
    @property
    def user(self):
        return attr(self, "request.user")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) or {}
        model = self.model
        model.class_permission = Permission.get_permission(self.user, model)
        context.update({
            'model': self.model,
            'model_name': self.model.__name__,
            'model_verbose_name': attr(ContentType.get_by_user_and_model(self.user, model), "verbose_name"),
        })
        return context
