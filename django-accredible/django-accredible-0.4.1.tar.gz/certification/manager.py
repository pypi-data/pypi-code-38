from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from .tasks import (
    CreateAccredibleGroupTask,
    CreateAccredibleConsultantRoleGroupTask,
    CreateAccredibleSimpleCredentialTask,
    CreateAccredibleGroupCredentialTask,
    DeleteAccredibleGroupTask,
    UpdateAccredibleGroupTask)


class CertificationGroupManager(models.Manager):

    def create_group(self, course_name, issued_on, **kwargs):

        group = self.create(**kwargs)

        if settings.ACCREDIBLE_ENABLED:
            CreateAccredibleGroupTask().s(
                group_id=group.pk,
                course_name=course_name,
                issued_on=issued_on).apply_async()

        return group

    def update_group(self, user_from, certification_group, **kwargs):
        if 'group_name' in kwargs:
            certification_group.name = kwargs['group_name']
        if 'description' in kwargs:
            certification_group.description = kwargs['description']
        certification_group.save(update_fields=['name', 'description'])

        if settings.ACCREDIBLE_ENABLED:
            UpdateAccredibleGroupTask().s(
                group_id=certification_group.pk,
                course_name=kwargs.get('course_name'),
                issued_on=kwargs.get('issued_on')).apply_async()

        return certification_group

    def remove_group(self, group):
        DeleteAccredibleGroupTask().s(
            group_id=group.pk).apply_async()

    def create_group_and_credentials(
            self, user_from, course_name, issued_on, **kwargs):
        credentials = []
        related_objects_list = kwargs.pop('related_objects_list')
        certification_group = self.create(**kwargs)

        for related_object in related_objects_list:
            credential = certification_group.credentials.create(
                user=related_object.user,
                content_type=ContentType.objects.get_for_model(related_object),
                object_id=related_object.pk)
            credentials.append(credential.pk)

        if settings.ACCREDIBLE_ENABLED and len(credentials):
            CreateAccredibleConsultantRoleGroupTask().s(
                group_id=certification_group.pk,
                issued_on=issued_on,
                course_name=course_name).apply_async()

        return certification_group

    def release_simple_credential(self, certification_group, user_from, certification_credential):

        if settings.ACCREDIBLE_ENABLED:
            CreateAccredibleSimpleCredentialTask().s(
                credential_id=certification_credential.pk).apply_async()
        return certification_credential

    def release_group_credential(self, user_from, certification_group, objects_list):

        credentials = []

        for related_object in objects_list:
            ct = ContentType.objects.get_for_model(related_object)
            credential = certification_group.credentials.create(
                user=related_object.user,
                content_type=ct,
                object_id=related_object.pk)
            credentials.append(credential.pk)

        if len(credentials) > 0 and settings.ACCREDIBLE_ENABLED:
            CreateAccredibleGroupCredentialTask().s(
                credentials_id=credentials).apply_async()
