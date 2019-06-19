from pbx_admin.options import ModelAdmin
from pbx_admin.sites import site, AdminSite


def register(*models, **kwargs):
    def _model_admin_wrapper(admin_class):
        if not models:
            raise ValueError("At least one model must be passed to register.")

        admin_site = kwargs.pop("site", site)

        if not isinstance(admin_site, AdminSite):
            raise ValueError("site must subclass AdminSite")

        if not issubclass(admin_class, ModelAdmin):
            raise ValueError("Wrapped class must subclass ModelAdmin.")

        admin_site.register(models, admin_class=admin_class, **kwargs)

        return admin_class

    return _model_admin_wrapper
