from django.db import models


class Position(models.Model):
    """
    A specific position held by candidates on an issue (e.g. "For A 10%
    Carbob Tax", "Against Medicare For All", etc.)
    """

    name = models.CharField(max_length=200)
    explanation = models.TextField(null=True, blank=True)
    issue = models.ForeignKey("Issue", on_delete=models.PROTECT)
    candidates = models.ManyToManyField("Candidate")
    order = models.IntegerField()

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ("name", "issue")
        ordering = ["order"]
