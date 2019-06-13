from django.db import models

from solo.models import SingletonModel


class CMISConfig(SingletonModel):
    client_url = models.URLField(default='http://localhost:8082/alfresco/cmisatom')
    client_user = models.CharField(max_length=200, default='admin')
    client_password = models.CharField(max_length=200, default='admin')
    locations = models.ManyToManyField('drc_cmis.CMISFolderLocation')

    def __str__(self):
        return "CMIS Configuration"

    class Meta:
        verbose_name = "CMIS Configuration"


class CMISFolderLocation(models.Model):
    location = models.CharField(max_length=200, default='')

    def __str__(self):
        return self.location
