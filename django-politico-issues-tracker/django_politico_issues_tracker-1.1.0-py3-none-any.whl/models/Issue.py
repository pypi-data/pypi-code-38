from django.db import models
from issuestracker.managers.live import LiveManager
from issuestracker.utils.storage_service import StorageService


class Issue(models.Model):
    """
    A specific issue of a category (e.g. "Medicare 4 All", "Carbon Tax", etc.)
    """

    name = models.CharField(max_length=100, null=True, blank=True, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    dek = models.TextField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    category = models.ForeignKey("Category", on_delete=models.PROTECT)
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
