from django.conf import settings
from django.db import models

from djangoldp.models import Model

class Skill(Model):
    name = models.CharField(max_length=255, default='')
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="skills")

    class Meta:
        permission_classes=[]
        serializer_fields=["@id", "name"]
        nested_fields=[]
        container_path = 'skills/'
        rdf_type = 'hd:skill'
        depth = 0


    def __str__(self):
        return self.name
