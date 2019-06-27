from celery import Task
from django.apps import apps

from ..accredible import groups, credentials


class CreateAccredibleConsultantRoleGroupTask(Task):
    ignore_result = True
    name = 'CreateAccredibleConsultantRoleGroupTask'

    def run(self, group_id, issued_on, course_name):
        CertificationGroup = apps.get_model('certification', 'CertificationGroup')
        group = CertificationGroup.objects.get(pk=group_id)
        group = groups.create_group(group, issued_on, course_name)
        credentials.create_group_credential(
            group.credentials.all(),
            group.instructor_name,
            group.accredible_id,
            issued_on=issued_on,
        )
