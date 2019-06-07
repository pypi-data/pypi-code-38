# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .models import BulmaContentModel


class djangocms_bulma_content(CMSPluginBase):
    """A short description of this plugin."""

    module = _('Generic')
    name = _('Bulma Element Content')
    model = BulmaContentModel
    render_template = 'cms/plugins/djangocms-bulma-content.html'
    text_enabled = True
    allow_children = True

    def render(self, context, instance, placeholder):
        context = super(djangocms_bulma_content, self) \
            .render(context, instance, placeholder)
        return context


plugin_pool.register_plugin(djangocms_bulma_content)
