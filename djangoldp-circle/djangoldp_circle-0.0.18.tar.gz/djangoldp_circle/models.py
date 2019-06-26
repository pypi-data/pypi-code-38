from django.conf import settings
from django.db import models
from djangoldp.permissions import AnonymousReadOnly

from djangoldp.models import Model


class Circle(Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)
    team = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="owned_circles", on_delete=models.DO_NOTHING)
    jabberID = models.CharField(max_length=255, blank=True, null=True)
    jabberRoom = models.BooleanField(default=True)

    class Meta:
        auto_author = 'owner'
        nested_fields = ["team"]
        permission_classes = [AnonymousReadOnly]
        container_path = 'circles/'
        rdf_type = 'hd:circle'
        depth = 0


    def __str__(self):
        return self.name
