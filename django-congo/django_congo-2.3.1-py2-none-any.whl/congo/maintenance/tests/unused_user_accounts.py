# -*- coding: utf-8 -*-
from congo.conf import settings
from congo.maintenance.tests import BaseTest
from datetime import timedelta
from django.apps import apps
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.translation import ugettext_lazy as _
from congo.templatetags.admin_utils import admin_change_url

class Test(BaseTest):
    def __init__(self):
        super(Test, self).__init__()
        self.description = _(u"Konta użytkowników , które nie były logowane przez co najmniej 90 dni")

    def _run(self, *args, **kwargs):
        model_name = settings.AUTH_USER_MODEL
        model = apps.get_model(*model_name.split('.', 1))

        login_date = timezone.now() - timedelta(days = 90)
        queryset = model.objects.filter(last_login__lt = login_date)

        result = not bool(queryset.count())
        details = ""

        for user in queryset:
            change_url = admin_change_url(user)
            last_login = date_format(user.last_login, 'SHORT_DATE_FORMAT')
            details += """<a href="%s">%s</a> (ID: %s, last login: %s)<br />""" % (change_url, user, user.id, last_login)

        return {
            'result': result,
            'details': details,
        }
