from celery import Task
from django.apps import apps

from ..accredible import credentials


class CreateAccredibleSimpleCredentialTask(Task):

    ignore_result = True
    name = 'CreateAccredibleSimpleCredentialTask'

    def run(self, credential_id):
        CertificationCredential = apps.get_model(
            'certification', 'CertificationCredential')
        credential = CertificationCredential.objects.get(pk=credential_id)
        instructor_name = credential.group.instructor_name
        credentials.create_simple_credential(credential, instructor_name)
