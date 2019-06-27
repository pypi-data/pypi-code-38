from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from model_utils.models import TimeStampedModel

from ..conf import settings
from ..manager import CertificationGroupManager


class CertificationGroup(TimeStampedModel):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        on_delete=models.deletion.CASCADE,
        related_name='certification_certificationgroup_related',
    )
    name = models.CharField(max_length=200)
    description = models.TextField(null=True)
    accredible_id = models.IntegerField(blank=True, null=True)
    design_id = models.IntegerField(blank=True, null=True)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
    )
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    _type = models.CharField(
        max_length=100,
        choices=settings.CERTIFICATION_CH_GROUP_CH_TYPE)
    status = models.CharField(
        max_length=1,
        choices=settings.CERTIFICATION_CH_GROUP_STATUS,
        default=settings.CERTIFICATION_CH_GROUP_STATUS_DEFAULT)
    objects = CertificationGroupManager()

    def __str__(self):
        return self.name

    @property
    def instructor_name(self):
        return self.content_object.created_by.get_full_name()
