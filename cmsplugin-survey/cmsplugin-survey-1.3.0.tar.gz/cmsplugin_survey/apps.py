from __future__ import unicode_literals

from appconf import AppConf
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class CmspluginSurveyConfig(AppConfig):
    name = 'cmsplugin_survey'
    verbose_name = _('django CMS Surveys')


class CmspluginSurveyAppConf(AppConf):
    TEMPLATES = [
        ('default', _('default')),
    ]

    class Meta:
        prefix = 'CMSPLUGIN_SURVEY'
