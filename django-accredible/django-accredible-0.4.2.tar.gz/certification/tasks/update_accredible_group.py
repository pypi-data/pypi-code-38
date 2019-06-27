from celery import Task
from django.apps import apps

from ..accredible import groups


class UpdateAccredibleGroupTask(Task):
    ignore_result = True
    name = 'UpdateAccredibleGroupTask'

    def run(self, group_id, issued_on, course_name):
        CertificationGroup = apps.get_model('certification', 'CertificationGroup')
        group = CertificationGroup.objects.get(pk=group_id)
        groups.update_group(group, issued_on=issued_on, course_name=course_name)
