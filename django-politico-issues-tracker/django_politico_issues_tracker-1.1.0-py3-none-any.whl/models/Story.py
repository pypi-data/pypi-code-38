from django.db import models


class Story(models.Model):
    """
    Related coverage about a given issue.
    """

    headline = models.CharField(max_length=200)
    link = models.URLField(max_length=200)
    issue = models.ForeignKey("Issue", on_delete=models.PROTECT)
    date_added = models.DateField(null=True, blank=True)
    order = models.IntegerField()

    def __str__(self):
        return self.headline

    class Meta:
        ordering = ["order"]
