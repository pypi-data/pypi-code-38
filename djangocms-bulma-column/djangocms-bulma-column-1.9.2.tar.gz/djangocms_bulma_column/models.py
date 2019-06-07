from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from cms.models import CMSPlugin
from cms.utils.compat.dj import python_2_unicode_compatible



@python_2_unicode_compatible
class MultiColumns(CMSPlugin):
    """
    A plugin that has sub Column classes
    """
    cmsplugin_ptr = models.OneToOneField(CMSPlugin,
        related_name='%(app_label)s_%(class)s', parent_link=True,
        on_delete=models.CASCADE)
    extra_css = models.CharField(_("extra_css"), max_length=150)

    def __str__(self):
        plugins = self.child_plugin_instances or []
        return _(u"%s columns") % len(plugins)


@python_2_unicode_compatible
class Column(CMSPlugin):
    """
    A Column for the MultiColumns Plugin
    """
    extra_css = models.CharField(_("extra_css"), max_length=150)
    cmsplugin_ptr = models.OneToOneField(
        CMSPlugin,
        related_name='%(app_label)s_%(class)s',
        parent_link=True,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return u"%s" % self.id
