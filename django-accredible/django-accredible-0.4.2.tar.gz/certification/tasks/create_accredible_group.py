from celery import Task
from django.apps import apps

from ..accredible import groups


class CreateAccredibleGroupTask(Task):
    ignore_result = True
    name = 'CreateAccredibleGroupTask'

    def run(self, group_id, issued_on, course_name):
        CertificationGroup = apps.get_model('certification', 'CertificationGroup')
        group = CertificationGroup.objects.get(pk=group_id)
        groups.create_group(group, issued_on, course_name)
