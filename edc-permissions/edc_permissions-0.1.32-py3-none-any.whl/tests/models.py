from django.db import models


class PiiModel(models.Model):

    name = models.CharField(max_length=50, null=True)

    class Meta:
        permissions = (("be_happy", "Can be happy"),)


class AuditorModel(models.Model):

    name = models.CharField(max_length=50, null=True)

    class Meta:
        permissions = (("be_sad", "Can be sad"),)
