from django.db import models
from issuestracker.managers.live import LiveManager
from issuestracker.utils.storage_service import StorageService


class Category(models.Model):
    """
    A broad category of issues (e.g. "Health Care", "Education", etc.)
    """

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    summary = models.TextField(null=True, blank=True)
    icon = models.URLField(max_length=200, null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    last_published = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=5,
        choices=(("draft", "Draft"), ("live", "Live")),
        default="draft",
    )

    objects = models.Manager()
    live = LiveManager()

    seo_name = models.CharField(max_length=100, null=True, blank=True)
    social_image = models.ImageField(
        upload_to="%Y/%m/", storage=StorageService(), null=True, blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
