# -*- coding: utf-8 -*-


from django.core.management import BaseCommand
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta

import json

from fcm_django.models import FCMDevice
from aparnik.utils.utils import get_request
from aparnik.contrib.settings.models import Setting
from aparnik.contrib.notifications.models import Notification
from aparnik.contrib.basemodels.api.serializers import ModelListPolymorphicSerializer
from aparnik.settings import aparnik_settings

User = get_user_model()
UserSummeryListSerializer = aparnik_settings.USER_SUMMARY_LIST_SERIALIZER


class Command(BaseCommand):
    # Show this when the user types help
    help = "send notification"

    # A command must define handle()
    def handle(self, *args, **options):

        start_time = now()

        if Notification.objects.update_needed().count() > 0:
            self.reindex()

        finished_time = now()

        print(('send notifications %s - time long: %ss.' % (now(), relativedelta(finished_time, start_time).seconds)))

    def reindex(self):
        icon = 'https://cdn.aparnik.com/static/website/img/logo-persian.png'
        request = get_request()
        try:
            setting = Setting.objects.get(key='LOGO_PROJECT_ICON')
            icon = setting.get_value()
        except:
            pass
        for obj in Notification.objects.update_needed():

            model_serial = json.dumps(ModelListPolymorphicSerializer(obj.model_obj,
                                                          many=False,
                                                          read_only=True,
                                                          context={'request': request},
                                                          ).data,
                                     sort_keys=True,
                                     indent=1,
                                     cls=DjangoJSONEncoder
                                     )  if obj.model_obj else None

            user_serial = json.dumps(UserSummeryListSerializer(obj.from_user_obj,
                                                               many=False,
                                                               read_only=True,
                                                               context={'request': request},
                                                               ).data,
                                     sort_keys=True,
                                     indent=1,
                                     cls=DjangoJSONEncoder
                                     ) if obj.from_user_obj else None
            try:
                devices = FCMDevice.objects.filter(user__in=obj.users.all()).order_by('device_id').distinct()
                # TODO: handle response to log and etc...
                sent_result = devices.send_message(
                    title=obj.title,
                    body=obj.description,
                    icon=icon,
                    data={
                        'model': model_serial,
                        'from_user': user_serial,
                        'type': obj.type,
                        'title': obj.title,
                        'description': obj.description,

                    }
                )
                obj.sent_result = sent_result
                obj.description_for_admin = None
                obj.update_needed = False
                obj.save()
            except Exception as inst:
                obj.description_for_admin = 'type: {0}\nargs: {1}\ninstance: {2}'.format(type(inst), inst.args, inst)
                obj.save()
