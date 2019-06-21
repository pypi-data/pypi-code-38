# -*- coding: utf-8 -*-


from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class InvitationConfig(AppConfig):
        name = 'aparnik.contrib.invitation'
        label = 'invitation'
        verbose_name = _('Invite')
