from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from appconf import AppConf


class CmspluginSurveyAppConf(AppConf):

    TEMPLATES = [
        ('default', _('default')),
    ]

    class Meta:
        prefix = 'CMSPLUGIN_SURVEY'
