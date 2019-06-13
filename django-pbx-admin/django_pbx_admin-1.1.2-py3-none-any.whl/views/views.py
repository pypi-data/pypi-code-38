from django.conf import settings
from django.views.generic import TemplateView

from pbx_admin.views.mixins import MessagesMixin
from pbx_admin.views import PermissionMixin


class IndexView(PermissionMixin, MessagesMixin, TemplateView):
    template_name = "pbx_admin/index.html"

    def get_context_groups(self, registry):
        groups = []
        for admin in registry:
            if admin.hide_from_index:
                continue
            if not any(admin.get_model_perms(self.request).values()):
                continue
            groups.append(
                {
                    "name": admin.opts.model_name,
                    "plural": admin.opts.verbose_name_plural,
                    "url": admin.list_url(),
                }
            )
        return groups

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        from pbx_admin.sites import site

        groups = self.get_context_groups(site.registry)

        context["groups"] = groups
        context["groups_num"] = len(groups)
        context["site_name"] = settings.PRINTBOX_SITE_NAME
        return context
