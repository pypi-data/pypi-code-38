from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from autoslug.fields import AutoSlugField
from jsonfield import JSONField
import collections


def get_current_site():
    return Site.objects.get_current().id


class CMSNamedMenu(models.Model):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(always_update=False,
                         populate_from='name',
                         unique=True)
    pages = JSONField(blank=True, null=True,
                      load_kwargs={
                          'object_hook': collections.OrderedDict
                      },
                      default=[])
    
    site = models.ForeignKey(Site,
                             on_delete=models.CASCADE,
                             help_text=_('The site the menu is accessible at.'),
                             verbose_name=_("site"),
                             default=get_current_site)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.__str__()

    class Meta:
        verbose_name = "CMS Menu"
        verbose_name_plural = "CMS Menus"
        unique_together = ('slug', 'site',)
