from celery import Task
from django.apps import apps

from ..accredible import credentials


class CreateAccredibleGroupCredentialTask(Task):

    ignore_result = True
    name = 'CreateAccredibleGroupCredentialTask'

    def run(self, credentials_id):
        CertificationCredential = apps.get_model('certification', 'CertificationCredential')
        user_credentials = CertificationCredential.objects.filter(id__in=credentials_id)
        instructor_name = user_credentials.first().group.instructor_name
        credentials.create_group_credential(user_credentials, instructor_name)
