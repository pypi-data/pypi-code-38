from django.db import models
from issuestracker.utils.storage_service import StorageService


class Candidate(models.Model):
    """
    Candidates with positions on issues.
    """

    uid = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    fec_uid = models.CharField(
        max_length=50, null=True, blank=True, unique=True
    )
    name = models.CharField(max_length=100)

    social_image = models.ImageField(
        upload_to="%Y/%m/", storage=StorageService(), null=True, blank=True
    )

    def __str__(self):
        return self.name
