from django.conf import settings
from django.contrib.auth import views as auth_views
from django.core.exceptions import ImproperlyConfigured
from django.db.models.base import ModelBase
from django.urls import path

from pbx_admin.options import ModelAdmin
from pbx_admin.views import views


class AdminSite:
    def __init__(self, name="pbx_admin"):
        self.registry = []
        self.name = name

    def register(self, model_or_iterable, admin_class=None, parent_model=None, **options):
        if not admin_class:
            admin_class = ModelAdmin

        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = [model_or_iterable]

        for model in model_or_iterable:
            if model._meta.abstract:
                raise ImproperlyConfigured(
                    f"The model {model.__name__} is abstract, "
                    f"so it cannot be registered with admin."
                )

            if options:
                admin_class = type(f"{model.__name__}Admin", (admin_class,), options)

            parent = None
            if parent_model:
                parent = self.get_admin(parent_model)

            self.registry.append(admin_class(model, self, parent=parent))

    def get_admin(self, model):
        try:
            for admin in self.registry:
                if admin.model == model:
                    return admin
        except KeyError:
            raise ImproperlyConfigured(f"The model {model.__name__} is not registered")

    def get_urls(self):
        # return top level model admins (without parent)
        urlpatterns = []
        for admin in self.registry:
            if not admin.parent:
                urlpatterns += admin.get_urls()
        urlpatterns += [
            path(
                "login/",
                auth_views.LoginView.as_view(
                    template_name="pbx_admin/login.html",
                    extra_context={"title": f"PBX2 {settings.PRINTBOX_SITE_NAME}"},
                ),
                name="login",
            ),
            path(
                "logout/",
                auth_views.LogoutView.as_view(
                    template_name="pbx_admin/logged_out.html",
                    extra_context={"title": f"PBX2 {settings.PRINTBOX_SITE_NAME}"},
                ),
                name="logout",
            ),
            path(r"", views.IndexView.as_view(), name="index"),
        ]
        return urlpatterns

    @property
    def urls(self):
        return self.get_urls(), "pbx_admin", self.name


site = AdminSite()
