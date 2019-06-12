# -*- coding:utf-8 -*-
__author__ = 'bee'

import json
import unicodecsv as csv
from django.http import StreamingHttpResponse
from bee_django_user.models import UserProfile
from django.conf import settings

from .models import UserSN


def get_max_student_id():
    user_profile_list = UserProfile.objects.filter(student_id__isnull=False).order_by("-student_id")
    if user_profile_list.exists():
        max_student_id = user_profile_list.first().student_id

    else:
        max_student_id = 0
    return max_student_id

def get_max_sn():
    sn_list = UserSN.objects.filter(is_used=True).order_by('start')
    if sn_list.exists():
        _sn=sn_list.first()
    else:
        return None
    end=_sn.end
    user_profile_list = UserProfile.objects.filter(sn__isnull=False,sn__lte=end).order_by("-sn")
    if user_profile_list.exists():
        max_sn = user_profile_list.first().sn
    else:
        max_sn = 0
    return max_sn

def get_user():
    user_list = UserProfile.objects.all()
    user_count = user_list.count()
    female_user_list = UserProfile.get_female_user_list()
    male_user_list = UserProfile.get_male_user_list()


def test():
    from  bee_django_course.models import UserLive
    from django.db.models import Count, Sum
    UserLive.objects.filter(status__in=[1, 2], record_status='10').values("user__userprofile__preuser__city").annotate(
        sum_duration=Sum("duration"), sum_user=Sum("user")).order_by('user__userprofile__preuser__city')

    # annotate(
    #     count_city=Count("user__userprofile__preuser__city")).order_by("-count_city")



# 导出csv
def export_csv(filename, headers, rows):
    response = StreamingHttpResponse((row for row in csv_itertor(headers, rows)), content_type="text/csv;charset=utf-8")
    response['Content-Disposition'] = 'attachment;filename="' + filename + '.csv"'
    return response


def csv_itertor(headers, rows):
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    yield writer.writerow(headers)
    for column in rows:
        yield writer.writerow(column)


class Echo(object):
    """An object that implements just the write method of the file-like
    interface.
    """

    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


# 完
