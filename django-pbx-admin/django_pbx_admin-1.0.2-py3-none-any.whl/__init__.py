from pbx_admin.decorators import register
from pbx_admin.options import ModelAdmin
from pbx_admin.sites import site, AdminSite

__all__ = ["register", "AdminSite", "site", "ModelAdmin"]

default_app_config = "pbx_admin.apps.AdminConfig"
